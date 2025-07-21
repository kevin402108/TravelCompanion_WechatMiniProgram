from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backEnd.app.database import get_database
from backEnd.app.models import Plan,Arrange, User
from backEnd.app.utils import exceptions
from backEnd.app.utils.logger import setup_logger

planGen_router = APIRouter()

logger = setup_logger("plan_generate_router")
MAX_DEADLOCK_RETRIES = 3  # 最大死锁重试次数
SINGLE_QUERY_TIMEOUT = 10.0
TOTAL_TIMEOUT = 60.0
BASE_RETRY_DELAY = 1.0
DEADLOCK_ERROR_CODES = (1213,)

class PlanRequestModel(BaseModel):
    user_id:int
    personality:str
    hobbies:str
    budget:str
    time:str
    preferences:str
    
@planGen_router.post(
    "/personal_plan_generate",
    summary="个性化旅游方案生成",
    response_description="符合用户个性化的旅游方案数据"
)
async def personalPlanGenerate(
    PlanRequest: PlanRequestModel,
    db: Session = Depends(get_database)
):
    # 验证用户是否存在
    user = db.query(User).filter(User.id == PlanRequest.user_id)
    if not user:
        raise exceptions.UserNotFoundError()
    db.commit()
    
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
            "detail":
            "从桂林出发，乘车前往阳朔（车程约1.5-2小时）。到达后入住民宿，稍作休息。下午开始十里画廊徒步，途经月亮山、剑峰山等景点，步行约4小时。晚上回到民宿，享受当地特色晚餐，体验阳朔的小镇氛围。",
        },
        {
            "title": "第二天：遇龙河漂流 & 探险",
            "detail":
            "早晨参加遇龙河竹筏漂流（漂流时间约2小时），欣赏沿途的自然山水。下午进行阳朔附近山洞探险，探索当地的溶洞和峡谷。晚上返回阳朔，享受晚餐并放松。",
        },
        {
            "title": "第三天：漓江徒步 & 返回",
            "detail":
            "早晨前往漓江边进行徒步，沿着漓江走，欣赏山水画般的景色。沿途经过一些宁静的村庄，适合拍照和放松。中午可以在当地的小镇上享用午餐，下午乘车返回,结束行程。",
        },
    ]
    
    # 往数据库添加生成的旅游方案记录
    try:
        with db.begin():
            new_plan = Plan(
                user_id = PlanRequest.user_id,
                personality = personality,
                hobbies = hobbies,
                duration = duration,
                budget = budget,
                preference = preference,
                total_spending = total_spending,
                arrange_data = arrange_detail
            )
            logger.info(f"开始往plan表插入新生成的个性化旅游方案 插入记录的详细信息:{new_plan}")
            db.add(new_plan)
            db.flush()
            
            logger.info(f"plan表插入新生成的旅游路线记录成功，新生成的个性化旅游方案id:{new_plan.id}")
            insertArrangment(db,arrange_detail)
            
            
    except Exception as e:
        db.rollback()
        raise exceptions.SQLExecutionError(str(e))

    response = {
        "data":{
            "plan":{
                "budget":total_spending,
                "arrange":arrange_detail
            }
        }
    }
    # zreturn response
    
    
def insertArrangment(db:Session,arrangement:list[dict[str,str]]) -> list[dict[int,str,str]]:
    pass
    

def userFeatureAnalysis(analysis_list:list):
    # 传入参数校验
    user_feature = []
    analysis_list_check(analysis_list)
    personality,hobbies,budget,travel_days,preference,current_time = analysis_list
    
    # 每个维度的选项所映射的标签
    tag_rule = {
        'personality':{
            "探索未知、寻找独特的旅行体验": ["探险", "深度体验"],
            "选择热门景点、享受热闹氛围": ["热门", "热爱社交"],
            "依赖朋友/家人的建议、避免过多选择": ["依赖", "省心出行"]
        },
        'preference':{
            "登山徒步": ["自然类", "户外运动"],
            "越野冒险": ["探险类", "极限运动"],
            "探索历史遗迹": ["人文类", "文化探索"],
            "参观名胜古迹": ["人文类", "经典景点"],
            "体验当地习俗文化": ["文化类", "在地体验"],
            "品尝美食": ["美食类", "特色饮食"]
        },
        'hobbies':{
            "徒步探险": ["自然类", "户外运动"],
            "沙滩休闲": ["休闲类", "度假偏好"],
            "美食体验": ["美食类", "特色饮食"],
            "参观博物馆": ["人文类", "文化探索"],
            "游玩主题乐园": ["休闲类", "亲子活动"]
        },
        'budget':{
            
        },
        'travel_days':{
            "短途旅行(1-3天)":["短途旅行","1-3天","周边游"],
            "中长途旅行(4-7天)":["中长途旅行","4-7天",""],
            "长途旅行(7天以上)":["长途旅行","7天以上",""],
        },
    }
    
            
            
def analysis_list_check(analysis_list: list):
    param_type = type(analysis_list)
    length = len(analysis_list)
    if param_type != list:
        raise exceptions.DataMismatchError(f"expect type 'list' but get type '{param_type}'")
    
    if length != 6:
        raise exceptions.DataError(f"期望传入的列表长度为6，但实际的列表长度为{length}")
    
    for idx,item in analysis_list:
        item_type = type(item)
        if idx == length-1:
            if item_type != datetime:
                raise exceptions.DataMismatchError(f"expect type 'datetime' but get type '{item_type}'")
        else:
            if item_type != str:
                raise exceptions.DataMismatchError(f"expect type 'str' but get type '{item_type}'")
                
    
        
        

        
    
    



    
      
    
        
    
    
    
    
    
    
    
    