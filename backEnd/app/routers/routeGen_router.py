import time
import traceback
from typing import List

from fastapi import APIRouter , Depends , HTTPException , Request
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from pydantic import BaseModel , field_validator
from sqlalchemy import insert, exc, delete
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from backEnd.app.database import get_database
from backEnd.app.models import Route , RouteSpotsMapping , Spots
from backEnd.app.utils import type_utils
from backEnd.app.utils.auth_utils import extractUserByVerifyCredential
from backEnd.app.utils.logger import setupLogger

# 配置
route_gen_router = APIRouter ( )
route_gen_logger = setupLogger ( "route_generate" , fileName = "route_generate.log" )
security_schema = HTTPBearer()

MAX_DEADLOCK_RETRIES = 3
SINGLE_QUERY_TIMEOUT = 10.0
TOTAL_TIMEOUT = 60.0
BASE_RETRY_DELAY = 1.0
DEADLOCK_ERROR_CODES = (1213 ,)


# 数据模型
class RouteGenerationRequest ( BaseModel ) :
    destination: str
    travelDays: int
    budget: int
    preferences: str

    @classmethod
    def validate_positive ( cls , value: int , field ) :
        if value <= 0 :
            raise ValueError ( f"{field.name} 必须大于 0" )
        return value

    @classmethod
    def validate_destination ( cls , value: str ) :
        if not value.strip ( ) :
            raise ValueError ( "目的地不能为空" )
        return value.strip ( )


# 辅助函数1
def convert_spot_ids ( spot_id_list: List [ str ] ) -> List [ int ] :
    """转换景点ID列表，严格校验输入"""
    if type_utils.is_none ( spot_id_list ) :
        raise ValueError ( "spot_id_list 不能为 None" )
    if not type_utils.is_type_of_list_of_str ( spot_id_list ) :
        raise ValueError ( "spot_id_list 必须是 List[str]" )

    converted: List [ int ] = [ ]  # 用于存储转换后的ID
    seen = set ( )  # 用于记录已出现的ID

    for idx , spot_id in enumerate ( spot_id_list , start = 1 ) :
        try :
            spot_int = int ( spot_id )
        except ValueError :
            raise ValueError ( f"第{idx}项 '{spot_id}' 不是有效整数" )

        if spot_int <= 0 or str ( spot_int ) != spot_id :
            raise ValueError ( f"第{idx}项必须为正整数且无前导零，实际值: '{spot_id}'" )
        if spot_int in seen :
            raise ValueError ( f"第{idx}项重复 ID: {spot_int}" )
        seen.add ( spot_int )
        converted.append ( spot_int )

    return converted

# 辅助函数2
def insertRouteSpotMapping ( db: Session , spot_id_list: list [ str ] , route_id: int ) :
    """ 并发安全的路线-景点关联插入"""
    start_time = time.time()
    converted_spot_ids = convert_spot_ids (spot_id_list)
    spotListsLength = len ( converted_spot_ids )

    try_times = 0
    while try_times < MAX_DEADLOCK_RETRIES :
        try :
            with db.begin_nested() :
                if time.time() - start_time > TOTAL_TIMEOUT :
                    raise TimeoutError ( "操作超时！" )
                existing_spot_ids = {
                    row [0] for row in db.query ( Spots.id )
                    .filter ( Spots.id.in_ ( converted_spot_ids ) )
                    .with_for_update()
                    .all()
                }

                # 查询景点是否存在
                missing_ids = set ( converted_spot_ids ) - existing_spot_ids
                if missing_ids :
                    error_msg = f"路线 {route_id} 存在无效景点ID: {missing_ids}"
                    route_gen_logger.error ( error_msg )
                    raise HTTPException ( status_code = 400 , detail = error_msg )

                # 查询已存在的映射关系，防止重复插入
                existing_mappings = {
                    mapping.spot_id for mapping in db.query ( RouteSpotsMapping.spot_id )
                    .filter ( RouteSpotsMapping.route_id == route_id ,
                              RouteSpotsMapping.spot_id.in_ ( converted_spot_ids ) )
                    .with_for_update ( )
                    .all ( )
                }
                newSpots = [ spot_id for spot_id in converted_spot_ids if spot_id not in existing_mappings ]

                if not newSpots :
                    route_gen_logger.warning ( f"route_id={route_id} 所有景点均已关联，无需插入" )
                    return

                # 插入新的映射关系
                stmt = insert ( RouteSpotsMapping ).values ( [
                    { "route_id" : route_id , "spot_id" : sid } for sid in newSpots
                ] ).prefix_with ( "IGNORE" )

                route_gen_logger.info ( f"开始往route_spot_mapping表插入包含景点映射关系" )
                result = db.execute ( stmt )
                insertRowNum = result.rowcount

                if insertRowNum == spotListsLength :
                    route_gen_logger.info ( f"route {route_id}：线路-景点映射插入成功,共插入{insertRowNum}条记录" )
                else :
                    error_msg = f"route {route_id}：线路-景点映射部分或全部插入失败,共插入{insertRowNum}条记录"
                    route_gen_logger.error ( error_msg )
                    raise HTTPException ( status_code = 500 , detail = error_msg )

        except (exc.OperationalError , exc.InternalError) as e :
            db.rollback ( )
            if hasattr ( e.orig , "args" ) and e.orig.args [ 0 ] in DEADLOCK_ERROR_CODES :
                if try_times < MAX_DEADLOCK_RETRIES :
                    delay = BASE_RETRY_DELAY * 2 * (2 ** try_times)
                    route_gen_logger.warning ( f"死锁重试: 路线 {route_id}, 第{try_times + 1}次重试 需等待{delay}秒" )
                    time.sleep ( delay )
                    try_times += 1
                    continue
                else :
                    route_gen_logger.error ( f"死锁重试次数超过上限!" )
                    raise HTTPException ( status_code = 503 , detail = "系统繁忙，请稍后重试!" )
            if e.orig.args [ 0 ] == 3024 :
                route_gen_logger.error ( f"数据库查询超时 route_id:{route_id}" )
                raise HTTPException ( status_code = 504 , detail = "数据库操作超时" )

            route_gen_logger.error ( f"数据库操作发生错误: 路线 {route_id}, 错误信息: {str ( e )}" )
            raise HTTPException ( status_code = 500 , detail = "数据库操作失败" )

        except TimeoutError :
            route_gen_logger.error ( f"TOTAL OPERATION TIMEOUT (route_id:{route_id})" )
            raise HTTPException ( status_code = 408 , detail = f"操作超时！(route_id:{route_id})" )
        except HTTPException as httpException :
            raise httpException
        except Exception as e :
            route_gen_logger.error ( f"未知错误: 路线 {route_id}, 错误详情: {traceback.format_exc ( )}" )
            raise HTTPException ( status_code = 500 , detail = "   服务器内部错误" )

# 辅助函数3
def get_route_spots_with_names(db: Session, route_id: int) -> List[dict]:
    """根据 route_id 查询关联的景点名称列表"""
    spots = db.query(Spots.id, Spots.name).join(
        RouteSpotsMapping,
        RouteSpotsMapping.spot_id == Spots.id
    ).filter(RouteSpotsMapping.route_id == route_id).all()
    return [{"id": sid, "name": name} for sid, name in spots]


# API：生成旅游路线 POST请求
@route_gen_router.post (
    "/routes/auto_generate" ,
    summary = "自动生成旅游路线" ,
    response_description = "包含推荐景点的路线数据" ,
)
def route_auto_generate (
        route_request_data: RouteGenerationRequest ,
        credentials: HTTPAuthorizationCredentials = Depends( security_schema ),
        db: Session = Depends ( get_database )
):
    try:
        with db.begin():
                user = extractUserByVerifyCredential(credentials,db)
                if user is None:
                    raise HTTPException(status_code = 404 , detail = "用户不存在")

                spot_ids = [ "1" , "2" , "3" , "4" , "6" ]
                new_route = Route(
                    user_id = user.id,
                    destination = route_request_data.destination ,
                    travel_days = route_request_data.travelDays ,
                    budget = route_request_data.budget ,
                    preference = route_request_data.preferences ,
                    route_description = None,
                    route_spots = spot_ids,
                )

                route_gen_logger.info ( f"开始往route表插入新生成的旅游路线记录 插入记录的详细信息:{new_route}"  )
                db.add(new_route)
                db.flush()

                route_gen_logger.info ( f"route表插入新生成的旅游路线记录成功，新生成的旅游路线id:{new_route.id}" )
                insertRouteSpotMapping (db,spot_ids,new_route.id)

                if db.query ( RouteSpotsMapping ).filter_by ( route_id = new_route.id ).count() == 0 :
                    route_gen_logger.error (f"route_id={new_route.id} 未插入任何关联数据" )
                    raise HTTPException ( 500 , detail = "数据插入失败!")

        response = {
            "data" : {
                "route" : {
                    "route_id" : new_route.id ,
                    "detail" : [
                        {
                            "id" : 1 ,
                            "name" : "遇龙河" ,
                            "description" : "遇龙河是一条较为宁静的河流，水流平缓，周围环绕着喀斯特山峰。您可以选择竹筏漂流或划船，享受水清山绿的宁静与美丽，远离游客的喧嚣，体验与大自然亲密接触的感觉。" ,
                        } ,
                        {
                            "id" : 2 ,
                            "name" : "漓江" ,
                            "description" : "漓江的山水景色被誉为世界上最美的河流之一。沿江的喀斯特山脉如画卷般展开，水面清澈，群山倒影。您可以选择竹筏漂流，或者在江边徒步，沉浸在这一片美丽的自然风光中。" ,
                        } ,
                        {
                            "id" : 3 ,
                            "name" : "龙脊梯田" ,
                            "description" : "位于桂林以北，龙脊梯田是一个少人打扰的景区，可以深入自然环境中，欣赏一望无际的梯田景色。每个季节的景色都不同，春天水田倒影，秋冬则是金黄的稻谷季节。" ,
                        } ,
                        {
                            "id" : 4 ,
                            "name" : "龙胜温泉" ,
                            "description" : "龙胜温泉位于桂林周边山区，远离喧嚣的城市，温泉水质优良，被群山环绕，是放松心情、恢复体力的好地方。环境安静，适合在大自然中休养生息。" ,
                        } ,
                        {
                            "id" : 6 ,
                            "name" : "黄布倒影" ,
                            "description" : "黄布倒影是漓江沿线的著名景点，因水中山的倒影形成了如画的景致。这里人少、风景美，是一个宁静的观光地，您可以在这里享受桂林山水的自然美。" ,
                        } ,
                    ]
                }
            }
        }
        return response
    except HTTPException:
        raise
    except Exception as e:
        route_gen_logger.error(f"事务回滚：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部错误")

# API: 删除旅游路线中指定景点 DELETE请求
@route_gen_router.delete(
    "/routes/{route_id}/spots/{spot_id}" ,
    summary = "删除旅游路线中指定景点" ,
    response_description = "删除景点成功"
)
def delete_route_spot(
        route_id: int ,
        spot_id: int ,
        credentials: HTTPAuthorizationCredentials = Depends(security_schema),
        db: Session = Depends(get_database)
):
   """
   删除指定路线中与某景点的关联关系。
   - 仅允许路线所属用户操作
   - 若关联不存在，返回成功（幂等）
   """
   try:
       user = extractUserByVerifyCredential(credentials,db)
       if user is None:
           route_gen_logger.warning(f"delete_route_spot: 用户未登录或凭证无效")
           raise HTTPException(status_code=401, detail="未授权访问!")

       route = db.query(Route).filter(Route.id == route_id, Route.user_id == user.id).first()
       if not route:
           route_gen_logger.warning(f"delete_route_spot: 路线 {route_id} 不存在或不属于当前用户，user_id={user.id}")
           raise HTTPException(status_code=404, detail="路线不存在或无权限")

       # 删除关联
       stmt_delete_map = delete(RouteSpotsMapping).where(
           RouteSpotsMapping.route_id == route_id,
           RouteSpotsMapping.spot_id == spot_id
       )
       result = db.execute(stmt_delete_map)
       deleted_count = result.rowcount

       if deleted_count > 0:
           route_gen_logger.info(f"delete_route_spot: 成功删除 route_id={route_id} 与 spot_id={spot_id} 的关联，共{deleted_count}条")

           current_spots = route.route_spots or []
           if str(spot_id) in current_spots:
               updated_spots = [sid for sid in current_spots if sid != str(spot_id)]
               route.route_spots = updated_spots
               route_gen_logger.info(f"delete_route_spot: 更新 route_spots: {current_spots} → {updated_spots}")
           else:
               route_gen_logger.warning(f"delete_route_spot: route_spots 中未找到 spot_id={spot_id}，但关联已删除（可能历史数据不一致）")
       db.commit()

       if deleted_count == 0:
           route_gen_logger.info(f"delete_route_spot: 关联 route_id={route_id}, spot_id={spot_id} 不存在，忽略删除")
       else:
           route_gen_logger.info(f"delete_route_spot: 成功删除 route_id={route_id} 与 spot_id={spot_id} 的关联，并更新 route_spots")
       return {"data": {"message": "删除成功", "deleted": deleted_count}}

   except Exception as e:
       route_gen_logger.error(f"delete_route_spot: SQL执行出错：{str(e)}")
       db.rollback()
       raise HTTPException(status_code=500, detail="服务器内部错误")

# API 获取用户生成的旅游路线 GET请求
@route_gen_router.get(
    "/routes",
    summary="获取当前用户历史规划路线",
    response_description="返回最近20条路线，含景点名称"
)
def get_user_routes(
    credentials: HTTPAuthorizationCredentials = Depends(security_schema),
    db: Session = Depends(get_database)
):
    try:
        user = extractUserByVerifyCredential(credentials, db)
        if not user:
            raise HTTPException(status_code=401, detail="未授权访问")

        stmt = select(Route).where(Route.user_id == user.id).order_by(Route.create_time.desc()).limit(20)
        routes = db.scalars(stmt).all()

        result = []
        for r in routes:
            # 获取景点名称列表
            spot_list = get_route_spots_with_names(db, r.id)
            result.append({
                "id": r.id,
                "destination": r.destination,
                "travel_days": r.travel_days,
                "budget": r.budget,
                "preference": r.preference,
                "create_time": r.create_time.strftime("%Y-%m-%d %H:%M:%S") if r.create_time else None,
                "spots": spot_list
            })
        route_gen_logger.info(f"get_user_routes: 返回 {len(result)} 条路线，含景点信息")
        return {"data": {"routes": result}}
    except HTTPException:
        raise
    except Exception as e:
        route_gen_logger.error(f"get_user_routes: SQL异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部错误")

@route_gen_router.delete("/routes/{route_id}")
def delete_route(
    route_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security_schema),
    db: Session = Depends(get_database)
):
    try:
        user = extractUserByVerifyCredential(credentials, db)
        if not user:
            route_gen_logger.warning(f"[delete_route] 用户未登录或凭证无效")
            raise HTTPException(status_code=401, detail="未授权")

        route = db.get(Route, route_id)
        if not route or route.user_id != user.id:
            route_gen_logger.warning(f"[delete_route] 路线 {route_id} 不存在或不属于当前用户")
            raise HTTPException(status_code=404, detail="路线不存在或无权限")
        db.execute(delete(RouteSpotsMapping).where(RouteSpotsMapping.route_id == route_id))
        db.delete(route)
        db.commit()

        route_gen_logger.info(f"[delete_route] 删除成功: route_id={route_id}")
        return {"data": {"message": "删除成功"}}

    except Exception as e:
        db.rollback()
        route_gen_logger.error(f"[delete_route] SQL执行出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除失败 - {str(e)}")


