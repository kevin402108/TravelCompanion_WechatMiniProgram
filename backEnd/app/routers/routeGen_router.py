import time
import traceback
from pydantic import BaseModel
from sqlalchemy import insert, text, exc
from backEnd.app.models import Route, RouteSpotsMapping, Spots, User
from backEnd.app.utils.logger import setup_logger
import backEnd.app.utils.exceptions as exceptions
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from backEnd.app.database import get_database
from backEnd.app.utils.exceptions import SpotIDListConversionError

routeGen_router = APIRouter()

logger = setup_logger("route_generate_router")
MAX_DEADLOCK_RETRIES = 3  # 最大死锁重试次数
SINGLE_QUERY_TIMEOUT = 10.0
TOTAL_TIMEOUT = 60.0
BASE_RETRY_DELAY = 1.0
DEADLOCK_ERROR_CODES = (1213,)


class RouteGenModel(BaseModel):
    id: int
    destination: str
    travelDays: int
    budget: int
    preferences: str


@routeGen_router.post(
    "/route_auto_generate",
    summary="自动生成旅游路线",
    response_description="包含推荐景点的路线数据",
)
async def routeAutoGenerate(
    RouteRequire: RouteGenModel, db: Session = Depends(get_database)
):
    user = db.query(User).filter(User.id == RouteRequire.id).first()
    if not user:
        raise exceptions.UserNotFoundError()
    db.commit()

    spot_ids = ["1", "2", "3", "4", "6"]
    try:
        with db.begin():
            new_route = Route(
                user_id=RouteRequire.id,
                destination=RouteRequire.destination,
                travel_days=RouteRequire.travelDays,
                budget=RouteRequire.budget,
                preference=RouteRequire.preferences,
                route_description=None,
                route_spots=spot_ids,
            )

            logger.info(f"开始往route表插入新生成的旅游路线记录 插入记录的详细信息:{new_route}")
            db.add(new_route)
            db.flush()
            
            logger.info(f"route表插入新生成的旅游路线记录成功，新生成的旅游路线id:{new_route.id}")
            insertRouteSpotMapping(db, spot_ids, new_route.id)
            
            if db.query(RouteSpotsMapping).filter_by(route_id=new_route.id).count() == 0:
                logger.error(f"route_id={new_route.id} 未插入任何关联数据")
                raise HTTPException(500, detail="数据插入失败!")
    except Exception as e:
        db.rollback()
        raise exceptions.SQLExecutionError(str(e))

    response = {
        "data": {
            "route": [
                {
                    "id": 1,
                    "name": "遇龙河",
                    "description": "遇龙河是一条较为宁静的河流，水流平缓，周围环绕着喀斯特山峰。您可以选择竹筏漂流或划船，享受水清山绿的宁静与美丽，远离游客的喧嚣，体验与大自然亲密接触的感觉。",
                },
                {
                    "id": 2,
                    "name": "漓江",
                    "description": "漓江的山水景色被誉为世界上最美的河流之一。沿江的喀斯特山脉如画卷般展开，水面清澈，群山倒影。您可以选择竹筏漂流，或者在江边徒步，沉浸在这一片美丽的自然风光中。",
                },
                {
                    "id": 3,
                    "name": "龙脊梯田",
                    "description": "位于桂林以北，龙脊梯田是一个少人打扰的景区，可以深入自然环境中，欣赏一望无际的梯田景色。每个季节的景色都不同，春天水田倒影，秋冬则是金黄的稻谷季节。",
                },
                {
                    "id": 4,
                    "name": "龙胜温泉",
                    "description": "龙胜温泉位于桂林周边山区，远离喧嚣的城市，温泉水质优良，被群山环绕，是放松心情、恢复体力的好地方。环境安静，适合在大自然中休养生息。",
                },
                {
                    "id": 6,
                    "name": "黄布倒影",
                    "description": "黄布倒影是漓江沿线的著名景点，因水中山的倒影形成了如画的景致。这里人少、风景美，是一个宁静的观光地，您可以在这里享受桂林山水的自然美。",
                },
            ]
        }
    }
    return response

def insertRouteSpotMapping(db: Session, spotIDList: list[str], route_id: int):
    """
    并发安全的路线-景点关联插入
    :param db: 数据库会话（复用主事务）
    :param route_id: 已创建的路线ID
    :param spot_ids: 景点ID列表（需验证有效性
    """
    start_time = time.time()
    converted_SpotIDList = safe_spotlist_convert(spotIDList)
    spotListsLength = len(converted_SpotIDList)
    
    try_times = 0

    while try_times < MAX_DEADLOCK_RETRIES:
        try:
            with db.begin_nested():
                if time.time() - start_time > TOTAL_TIMEOUT:
                    raise TimeoutError("操作超时！")
                existing = (
                    db.query(Spots.id)
                    .filter(Spots.id.in_(converted_SpotIDList))
                    .with_for_update()
                    .all()
                )

                # 确保所有id均存在
                existingIDs = {row[0] for row in existing}
                if missingIDs := set(converted_SpotIDList) - existingIDs:
                    error_msg = f"route {route_id} 存在无效景点ID:{missingIDs}"
                    logger.error(error_msg)
                    raise HTTPException(status_code=400, detail=error_msg)
                
                # 查询已存在的映射关系，防止重复插入
                existing_mapping =db.query(RouteSpotsMapping.spot_id).filter(
                    RouteSpotsMapping.route_id == route_id,
                    RouteSpotsMapping.spot_id.in_(converted_SpotIDList)
                ).with_for_update().all()
                existingSpots = {mapping.spot_id for mapping in existing_mapping}
                newSpots = [spotIDs for spotIDs in converted_SpotIDList if spotIDs not in existingSpots]
                
                if not newSpots:
                    logger.warning(f"route_id={route_id} 所有景点均已关联，无需插入")
                    return
                
                stmt = insert(RouteSpotsMapping).values(
                    [
                        {"route_id": route_id, "spot_id": sid}
                        for sid in newSpots
                    ]
                ).prefix_with("IGNORE")
                
                logger.info(f"开始往route_spot_mapping表插入 route_id={route_id}所包含的所有景点映射，景点列表:{newSpots}")
                result = db.execute(stmt)
                insertRowNum = result.rowcount
                if insertRowNum == spotListsLength:
                    logger.info(
                        f"route {route_id}：线路-景点映射插入成功,共插入{insertRowNum}条记录"
                    )
                else:
                    msg = f"route {route_id}：线路-景点映射部分或全部插入失败,共插入{insertRowNum}条记录"
                    logger.error(msg)
                    raise HTTPException(status_code=500, detail=msg)

        except (exc.OperationalError, exc.InternalError) as e:
            db.rollback()   

            if hasattr(e.orig, "args") and e.orig.args[0] in DEADLOCK_ERROR_CODES:
                if try_times < MAX_DEADLOCK_RETRIES:
                    delay = BASE_RETRY_DELAY * 2 * (2**try_times)
                    logger.warning(
                        f"DEADLOCK_RETRY route_id:{route_id} 第{try_times+1}次重试 需等待{delay}秒"
                        f"{traceback.format_exc()}"
                    )
                    time.sleep(delay)
                    try_times += 1
                    continue

                else:
                    logger.error(
                        f"DELOCK RETRY TIMES EXCEED route_id:{route_id} MAX_DEADLOCK_RETRIES_TIMES:{MAX_DEADLOCK_RETRIES}"
                    )
                    raise HTTPException(status_code=503, detail="系统繁忙，请稍后重试!")

            if e.orig.args[0] == 3024:
                logger.error(f"QUERY TIMEOUT route_id:{route_id}")
                raise HTTPException(status_code=504, detail="数据库操作超时")

            logger.error(
                f"UNKNOWN DATABASE ERROR OCCURED:{str(e)} (route_id:{route_id})"
            )

        except TimeoutError:
            logger.error(f"TOTAL OPERATION TIMEOUT (route_id:{route_id})")
            raise HTTPException(
                status_code=408, detail=f"操作超时！(route_id:{route_id})"
            )

        except HTTPException as httpException:
            raise httpException

        except Exception as e:
            logger.error(
                f"UNKNOWN ERROR(route_id:{route_id})\n{traceback.format_exc()}"
            )
            raise HTTPException(status_code=500, detail="未知错误")


def safe_spotlist_convert(spot_ids: list[str]) -> list[int]:
    if not spot_ids:
        raise ValueError("景点列表不能为空！")

    if not isinstance(spot_ids, list):
        raise TypeError(
            f"函数 safe_spotlist_convert 的参数类型为 list ,但实际接收到的参数类型为 {type(spot_ids).__name__}"
        )

    convert_result = []  # 用于存储转换后的景点列表
    existSpotID = set()  # 用于存储去重后的列表，作为源列表是否存在重复元素的参考

    for idx, spot_id in enumerate(spot_ids):
        try:
            if not isinstance(spot_id, str):
                raise TypeError(
                    f"expected element type 'str' but get '{type(spot_id).__name__}'"
                )

            spot_id_int = int(spot_id)

            if spot_id_int <= 0 or str(spot_id_int) != spot_id:
                raise ValueError(
                    f"第{idx+1}个元素必须为正整数且不含前导零，实际值：{spot_id}"
                )

            if spot_id_int not in existSpotID:
                existSpotID.add(spot_id_int)
                convert_result.append(spot_id_int)
            else:
                raise ValueError(f"列表中包含重复id：{spot_id_int}！")

        except (ValueError, TypeError) as e:
            raise SpotIDListConversionError(
                original_error=e, invalid_str=spot_id, pos=idx + 1
            ) from e

    return convert_result
