import time
from datetime import datetime
from typing import List , Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from pydantic import BaseModel
from sqlalchemy import exc
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import insert , select , delete

from backEnd.app.database import get_database
from backEnd.app.models import Plan,Arrange, User
from backEnd.app.utils import exceptions
from backEnd.app.utils.auth_utils import extractUserByVerifyCredential
from backEnd.app.utils.logger import setupLogger

planGen_router = APIRouter()
planGenLogger = setupLogger( "plan_generate_router" , fileName= "plan_generate.log" )
security_scheme = HTTPBearer()

MAX_DEADLOCK_RETRIES = 3  # 最大死锁重试次数
SINGLE_QUERY_TIMEOUT = 10.0
TOTAL_TIMEOUT = 60.0
BASE_RETRY_DELAY = 1.0
DEADLOCK_ERROR_CODES = (1213,)

class PlanRequestModel(BaseModel):
    personality:str
    hobbies:str
    budget:str
    duration:str
    preferences:str

# def analysis_list_check(analysis_list: list):
#     param_type = type(analysis_list)
#     length = len(analysis_list)
#     if param_type != list:
#         raise exceptions.DataMismatchError(f"expect type 'list' but get type '{param_type}'")
#
#     if length != 6:
#         raise exceptions.DataError(f"期望传入的列表长度为6，但实际的列表长度为{length}")
#
#     for idx,item in analysis_list:
#         item_type = type(item)
#         if idx == length-1:
#             if item_type != datetime:
#                 raise exceptions.DataMismatchError(f"expect type 'datetime' but get type '{item_type}'")
#         else:
#             if item_type != str:
#                 raise exceptions.DataMismatchError(f"expect type 'str' but get type '{item_type}'")

def insertArrangement( db: Session , arrangement: List[Dict[str, str]],plan_id: int) -> None:
    """
    插入行程安排到 Arrange 表
    - 根据 title 中的“第X天”自动提取 day（如“第一天”→1）
    - 若无法提取，则按列表索引 + 1 作为 day
    - 确保 plan_id + day 唯一性
    """
    if not arrangement:
        planGenLogger.warning(f"insertArrangement: arrangement 为空，plan_id={plan_id}")
        return

    try_times = 0
    while try_times < MAX_DEADLOCK_RETRIES:
        try:
            with db.begin_nested():
                records = []
                for idx, item in enumerate(arrangement):
                    title = item.get("title", "")
                    detail = item.get("detail", "")

                    day = None
                    if "第" in title and "天" in title:
                        import re
                        match = re.search(r"第(\d+)天", title)
                        if match:
                            day = int(match.group(1))
                    if day is None:
                        day = idx + 1

                    records.append({
                        "plan_id": plan_id,
                        "day": day,
                        "title": title[:50],
                        "detail": detail
                    })

                stmt = insert(Arrange).values(records)
                result = db.execute(stmt)
                inserted_count = result.rowcount

                planGenLogger.info(
                    f"plan_id={plan_id}：成功插入 {inserted_count} 条行程安排记录（day 范围: {min(r['day'] for r in records)}-{max(r['day'] for r in records)})"
                )
                return

        except (exc.OperationalError, exc.InternalError) as e:
            db.rollback()
            if hasattr(e.orig, "args") and e.orig.args[0] in DEADLOCK_ERROR_CODES:
                if try_times < MAX_DEADLOCK_RETRIES:
                    delay = BASE_RETRY_DELAY * (2 ** try_times)
                    planGenLogger.warning(
                        f"死锁重试：plan_id={plan_id}，第{try_times+1}次, 等待{delay}s"
                    )
                    time.sleep(delay)
                    try_times += 1
                    continue
                else:
                    planGenLogger.error(f"死锁重试超限：plan_id={plan_id}")
                    raise HTTPException(status_code=503, detail="系统繁忙，请稍后重试")
            raise HTTPException(status_code=500, detail="数据库操作失败")

        except Exception as e:
            planGenLogger.error(f"insertArrangement 错误：plan_id={plan_id}, error={str(e)}")
            raise HTTPException(status_code=500, detail="插入行程安排失败")

@planGen_router.post(
    "/travelPlans",
    summary="个性化旅游方案生成",
    response_description="符合用户个性化的旅游方案数据"
)
def createPersonalTravelPlan(
    PlanRequest: PlanRequestModel,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_database)
):
    try:
        # 验证用户是否存在
        user = extractUserByVerifyCredential(credentials,db)
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 分析用户特征
        now = datetime.now()
        # analysis_list = list(PlanRequest.model_dump().values())
        # userFeatureAnalysis(analysis_list)

        # 为用户搜索符合用户需求的个性化方案
        personality = ""
        hobbies=""
        duration = "1-3天"
        budget = '1000-3000元'
        preference = '登山徒步'
        total_spending = 1500
        arrange_detail = [
            {
                "title": "第一天：阳朔 & 自由探险",
                "detail":"从桂林出发，乘车前往阳朔（车程约1.5-2小时）。到达后入住民宿，稍作休息。下午开始十里画廊徒步，途经月亮山、剑峰山等景点，步行约4小时。晚上回到民宿，享受当地特色晚餐，体验阳朔的小镇氛围。",
            },
            {
                "title": "第二天：遇龙河漂流 & 探险",
                "detail":"早晨参加遇龙河竹筏漂流（漂流时间约2小时），欣赏沿途的自然山水。下午进行阳朔附近山洞探险，探索当地的溶洞和峡谷。晚上返回阳朔，享受晚餐并放松。",
            },
            {
                "title": "第三天：漓江徒步 & 返回",
                "detail":"早晨前往漓江边进行徒步，沿着漓江走，欣赏山水画般的景色。沿途经过一些宁静的村庄，适合拍照和放松。中午可以在当地的小镇上享用午餐，下午乘车返回,结束行程。",
            },
        ]

        new_plan = Plan(
            user_id = user.id,
            personality = personality,
            hobbies = hobbies,
            duration = duration,
            budget = budget,
            preference = preference,
            total_spending = total_spending,
            arrange_data = arrange_detail
        )
        planGenLogger.info( f"开始往plan表插入新生成的个性化旅游方案" )
        db.add(new_plan)
        db.flush()

        planGenLogger.info( f"plan表插入新生成的旅游路线记录成功，新生成的个性化旅游方案id:{new_plan.id}")
        insertArrangement(db,arrange_detail,new_plan.id)

        response = {
            "data":{
                "plan":{
                    "budget":total_spending,
                    "arrange":arrange_detail
                }
            }
        }
        return response
    except HTTPException as e:
        db.rollback()
        planGenLogger.error( f"plan表插入新生成的旅游路线记录失败，失败原因:{e.detail}" )
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@planGen_router.get("/plans", summary="获取用户历史个性化方案")
def get_user_plans(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_database)
):
    try:
        user = extractUserByVerifyCredential(credentials, db)
        if not user:
            planGenLogger.warning("get_user_plans: 用户未认证")
            raise HTTPException(status_code=401, detail="未授权访问")

        stmt = select(Plan).where(Plan.user_id == user.id).order_by(Plan.create_time.desc()).limit(20)
        plans = db.scalars(stmt).all()

        result = []
        for p in plans:
            try:
                arrange_list = db.query(Arrange.title, Arrange.detail).filter(Arrange.plan_id == p.id).order_by(Arrange.day).all()
                arrange_detail = [{"title": t, "detail": d} for t, d in arrange_list]
            except Exception as e:
                planGenLogger.error(f"get_user_plans: 查询 Plan(id={p.id}) 的行程安排失败", exc_info=True)
                arrange_detail = []

            result.append({
                "id": p.id,
                "budget": p.budget,
                "duration": p.duration,
                "preference": p.preference,
                "create_time": p.create_time.strftime("%Y-%m-%d %H:%M:%S") if p.create_time else None,
                "arrange": arrange_detail
            })

        planGenLogger.info(f"get_user_plans: 返回 {len(result)} 条个性化方案，user_id={user.id}")
        return {"data": {"plans": result}}
    except HTTPException:
        raise
    except Exception as e:
        planGenLogger.error(f"get_user_plans: SQL查询异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部错误")



@planGen_router.delete("/plans/{plan_id}", summary="删除个性化方案")
def delete_plan(
    plan_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_database)
):
    try:
        user = extractUserByVerifyCredential(credentials, db)
        if not user:
            planGenLogger.warning(f"delete_plan: 用户未认证，plan_id={plan_id}")
            raise HTTPException(status_code=401, detail="未授权访问")

        plan = db.get(Plan, plan_id)
        if not plan:
            planGenLogger.warning(f"delete_plan: 旅游方案{plan_id}不存在")
            raise HTTPException(status_code=404, detail="方案不存在")
        if plan.user_id != user.id:
            planGenLogger.warning(f"delete_plan: 用户{user.id}无权限删除方案{plan_id}")
            raise HTTPException(status_code=403, detail="无权限操作")

        deleted_arrange = db.execute(delete(Arrange).where(Arrange.plan_id == plan_id)).rowcount
        db.delete(plan)
        db.commit()

        planGenLogger.info(
            f"delete_plan: 删除成功 plan_id={plan_id}, 关联行程数={deleted_arrange}, user_id={user.id}"
        )
        return {"data": {"message": "删除成功"}}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        planGenLogger.error(
            f"delete_plan: 删除失败 plan_id={plan_id}, error={str(e)}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="删除失败，请重试")


    


                
    
        
        

        
    
    



    
      
    
        
    
    
    
    
    
    
    
    