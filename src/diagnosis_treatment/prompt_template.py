# Copyright (c) 2025,  IEIT SYSTEMS Co.,Ltd.  All rights reserved

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import yaml
from jinja2 import Template
from fastapi import HTTPException

import collections
VersionedPromptFactory = collections.defaultdict(dict)

format_distribute="""[
    {
        "患者意图": ""
    }
]
"""

format_client_select="""{
    "就诊人姓名": ""
}"""

format_client_info="""{
    "档案": {
        "患者信息": {
            "姓名": "",
            "是否儿童": "",
            "性别": "",
            "年龄": "",
            "出生日期": {
                "年": "",
                "月": "",
                "日":""
            },
            "证件类型": "",
            "证件号码": "",
            "手机号码": "",
            "所居区域": {
                "省": "",
                "市": "",
                "区": "",
                "街道": ""
            },
            "详细地址": ""
        },
        "监护人信息": {
            "姓名": "",
            "证件类型": "",
            "证件号码": ""
        }
    }
}
"""

#病历
format_basic_medical_record="""{
    "主诉": "",
    "现病史": "",
    "既往史": "xxx,xxx,xxx",
    "个人史": "xxx;xxx",
    "过敏史": "xxx;xxx;xxx"
}
"""

#科室
format_department_single="""[
    {
        "科室编号": "001",
        "科室名称": ""
    }
]
"""
format_department_multi="""[
    {
        "科室编号": "001",
        "科室名称": ""
    },
    {
        "科室编号": "002",
        "科室名称": ""
    }
]
"""

#挂号
format_hospital_register="""[{
    "科室编号": "",
    "科室名称": "",
    "医生编号": "",
    "医生姓名": "",
    "医生职称": "",
    "挂号日期": "",
    "起始时间": "",
    "终止时间": "",
    "号源数量": "",
    }
]
"""

format_hospital_register_modify="""[{"科室名称": "","医生姓名": "","挂号日期": "","起始时间": "","终止时间": "","号源数量": ""}]"""

REGISTER_MODEL_TYPE_BASE = "register_type_base"
REGISTER_MODEL_TYPE_INTENTION = "register_type_intention"

register_intention_json_str = '''
{
    "意图类型": "",
    "科室名称": "",
    "医生姓名": "",
    "医生职称": "",
    "日期": "",
    "时间": "",
    "号源": "",
    "查询主体": "",
    "优先级": ""
}
'''

register_intention_field_mapping = {
    "意图类型": "intention_tpye",
    "科室名称": "department_name",
    "医生姓名": "doctor_name",
    "医生职称": "doctor_title",
    "日期": "register_date",
    "时间": "register_time",
    "号源": "register_source",
    "查询主体": "query_subject",
    "优先级": "priority"
}


#诊断
format_diagnose="""{
"诊断": [{
       "诊断名称": "痛风",
       "诊断编码": "M10.900",
       "诊断标识": "疑似"
    },
    {
       "诊断名称": "关节炎",
       "诊断编码": "M13.900",
       "诊断标识": "疑似"
    }]
}
"""

#检查和化验
format_examine_assay="""{
"检查": [{
       "检查编号": "",
       "检查类型": "",
       "检查名称": "",
       "针对疾病": [
           {
               "诊断名称": ""
           }
       ],
       "开单数量": "1"
    }],
"化验": [{
        "项目编号": "JY8110",
        "项目类型": "临检类",
        "项目名称": "血常规（五分类）",
        "针对疾病": [
            {
                "诊断名称": ""
            }
        ],
        "开单数量": "1"
    }]
}
"""

#处方
format_prescription="""{
"处方": [{
    "药品编号": "YP123456",
    "药品名称": "维生素C片",
    "药品规格": "0.1g*100",
    "厂家名称": "XXXXXXXX制药厂",
    "开单数量": "10",
    "开单单位": "粒",
    "用药途径": "口服",
    "单次剂量": "1粒",
    "持续天数": "7天",
    "用药频次": "每日3次",
    "针对疾病": "",
    "药品作用": ""
},
{
    "药品编号": "YP123457",
    "药品名称": "",
    "药品规格": "0.1g*100",
    "厂家名称": "XXXXXXXX制药厂",
    "开单数量": "10",
    "开单单位": "粒",
    "用药途径": "口服",
    "单次剂量": "1粒",
    "持续天数": "7天",
    "用药频次": "每日3次",
    "针对疾病": "",
    "药品作用": ""
},
{
    "药品编号": "YP123458",
    "药品名称": "",
    "药品规格": "0.1g*100",
    "厂家名称": "XXXXXXXX制药厂",
    "开单数量": "10",
    "开单单位": "粒",
    "用药途径": "口服",
    "单次剂量": "1粒",
    "持续天数": "7天",
    "用药频次": "每日3次",
    "针对疾病": "",
    "药品作用": ""
}]}
"""

#输液
format_transfusion="""{
"输液": [{
    "药品编号": "ZS123456",
    "药品名称": "维生素C注射液",
    "药品规格": "0.5g*10*2ml",
    "厂家名称": "XXXXXXXX制药股份有限公司",
    "开单数量": "1",
    "开单单位": "支",
    "用药途径": "静脉滴注",
    "单次剂量": "1支",
    "持续天数": "1天",
    "用药频次": "每日1次",
    "针对疾病": "",
    "药品作用": "",
    "输液分组": "第一组",
    "输液速度": "30gtt/min"
},
{
    "药品编号": "ZS123457",
    "药品名称": "",
    "药品规格": "0.5g*10*2ml",
    "厂家名称": "XXXXXXXX制药股份有限公司",
    "开单数量": "1",
    "开单单位": "支",
    "用药途径": "静脉滴注",
    "单次剂量": "1支",
    "持续天数": "1天",
    "用药频次": "每日1次",
    "针对疾病": "",
    "药品作用": "",
    "输液分组": "第一组",
    "输液速度": "30gtt/min"
}]}
"""

#处置
format_disposition="""{
    "处置": [{
        "项目编号": "CZ123457",
        "项目名称": "换药",
        "频次": "Qd",
        "单次用量": "1",
        "持续时间": "1天"
    },
    {
        "项目编号": "CZ123457",
        "项目名称": "",
        "频次": "Qd",
        "单次用量": "1",
        "持续时间": "1天"
    }]
}
"""

#多方案-挑选
format_pick_therapy="""[
    {
        "方案名称": "",
        "方案解读": ""
    },
    {
        "方案名称": "",
        "方案解读": ""
    }
]
"""

#多方案-生成
format_generate_therapy="""{
    "治疗方案": [{
       "治疗编号": "001",
       "治疗类型": "",
       "治疗名称": "",
       "针对疾病": "",
       "潜在风险": "",
       "治疗计划": "xxx;xxx;xxx;"
    },
    {
       "治疗编号": "002",
       "治疗类型": "",
       "治疗名称": "",
       "针对疾病": "",
       "潜在风险": "",
       "治疗计划": "xxx;xxx;xxx;"
    }]
}
"""

#多方案-治疗
format_generate_medicine="""
{
"处方":[
{
"药品编号":"YP123456",
"药品名称":"维生素C片",
"药品规格":"0.1g*100",
"厂家名称":"XXXXXXXX制药厂",
"开单数量":"10",
"开单单位":"粒",
"用药途径":"口服",
"单次剂量":"1粒",
"持续天数":"7天",
"用药频次":"每日3次",
"针对疾病":"",
"药品作用":""
},
{
"药品编号":"YP123457",
"药品名称":"",
"药品规格":"0.1g*100",
"厂家名称":"XXXXXXXX制药厂",
"开单数量":"10",
"开单单位":"粒",
"用药途径":"口服",
"单次剂量":"1粒",
"持续天数":"7天",
"用药频次":"每日3次",
"针对疾病":"",
"药品作用":""
},
{
"药品编号":"YP123458",
"药品名称":"",
"药品规格":"0.1g*100",
"厂家名称":"XXXXXXXX制药厂",
"开单数量":"10",
"开单单位":"粒",
"用药途径":"口服",
"单次剂量":"1粒",
"持续天数":"7天",
"用药频次":"每日3次",
"针对疾病":"",
"药品作用":""
}
],
"输液":[
{
"药品编号":"ZS123456",
"药品名称":"维生素C注射液",
"药品规格":"0.5g*10*2ml",
"厂家名称":"XXXXXXXX制药股份有限公司",
"开单数量":"1",
"开单单位":"支",
"用药途径":"静脉滴注",
"单次剂量":"1支",
"持续天数":"1天",
"用药频次":"每日1次",
"针对疾病":"",
"药品作用":"",
"输液分组":"第一组",
"输液速度":"30gtt/min"
},
{
"药品编号":"ZS123457",
"药品名称":"",
"药品规格":"0.5g*10*2ml",
"厂家名称":"XXXXXXXX制药股份有限公司",
"开单数量":"1",
"开单单位":"支",
"用药途径":"静脉滴注",
"单次剂量":"1支",
"持续天数":"1天",
"用药频次":"每日1次",
"针对疾病":"",
"药品作用":"",
"输液分组":"第一组",
"输液速度":"30gtt/min"
}
],
"处置":[
{
"项目编号":"CZ123457",
"项目名称":"换药",
"频次":"Qd",
"单次用量":"1",
"持续时间":"1天"
},
{
"项目编号":"CZ123457",
"项目名称":"",
"频次":"Qd",
"单次用量":"1",
"持续时间":"1天"
}
]
}
"""


#复诊
format_return_visit="""{
    "病情总结": "",
    "是否复诊": ""
}
"""

#导诊
format_hospital_guide1="""{
"病历": {
    "主诉": ""
    },
"推荐科室": [
    {
        "科室编号": "001",
        "科室名称": ""
    }]
}
"""
format_hospital_guide2="""{
"病历": {
    "主诉": ""
    },
"推荐科室": [
    {
        "科室编号": "001",
        "科室名称": ""
    },
    {
        "科室编号": "002",
        "科室名称": ""
    }]
}
"""

gender_map={"男": "女", "女": "男"}

format_translate = {"原句":"", "翻译结果":""}

medical_fields={
    "主诉":"chief_complaint",
    "现病史":"history_of_present_illness",
    "既往史":"past_medical_history",
    "个人史":"personal_history",
    "过敏史":"allergy_history",
    "体格检查":"physical_examination",
    "辅助检查":"auxiliary_examination",
    "专科检查":"specialty_examination",
    "治疗":"cure",
    "医嘱":"doctor_advice"
}
reversed_medical_fields={v: k for k, v in medical_fields.items()}

sub_medical_fields={
    "体温":"temperature",
    "脉搏":"pulse",
    "血压":"blood_pressure",
    "呼吸":"respiration"
}
reversed_sub_medical_fields={v: k for k, v in sub_medical_fields.items()}

therapy_scheme_fields= {
    "保守治疗": "default_therapy",
    "手术治疗": "surgical_therapy",
    "化疗": "chemo_therapy",
    "放疗": "radiation_therapy",
    "心理治疗": "psycho_therapy",
    "康复治疗": "rehabilitation_therapy",
    "物理治疗": "physical_therapy",
    "替代疗法": "alternative_therapy",
    "观察治疗": "observation_therapy"
}
reversed_therapy_scheme_fields={v: k for k, v in therapy_scheme_fields.items()}

request_type_map={
   "distribute": "v0",
   "clientinfo": "v1",
   "basicmedicalrecord": "v2",
   "hospitalregister": "v3",
   "diagnosis": "v4",
   "examass": "v5",
   "scheme": "v6",
   "returnvisit": "v7",
   "hospitalguide": "v8",
   "doctormedicalrecord": "v9"
}

#问候语
greetings_prompt="您好，请详细描述您的症状，主要说明哪里不舒服，持续了多久。可以参考以下案例来描述：\
\n<span style='color: blue'>“胃痉挛，胃部隐痛，上腹部疼痛，持续一天</span>”"

#每句后添加的
single_add_prompt="\n每次只提问一个问题。"
single_max_round="\n请生成病历。"
single_min_round="请问您还有其他补充的吗？"
first_round="您的就诊档案已经建立成功，欢迎您来我院就诊，期望我们可以帮助到您。"
irrelevant_content="\n如果我提到了与当前任务不相关的话题，必须给出不要讨论无关话题的提醒。"
#multi_agent_prompt="\n如果我有表达“建档、预问诊、挂号、缴费、报告查询”的意思，你需要直接返回【XXX链接】。\
#例如：【建档链接】、【预问诊链接】、【挂号链接】、【缴费链接】、【报告查询链接】。返回链接时先说“我为您找到了如下链接：”。"
multi_agent_prompt=""

stop_sign = [
    '现在为您返回',
    '已经为您生成了预问诊报告，如无问题，请点击确认',
    '如下预约就诊，您看是否可以？',
    '抱歉，目前没有查询到'
]

format_new_regiter_info = "新挂号"
format_register_first_info = "我们为您推荐如下预约就诊"

class PromptTemplate():
    def __init__(self) -> None:
        self.prompt = {}
        self.format_distribute = format_distribute
        self.format_client_select = format_client_select
        self.format_client_info = format_client_info
        self.format_basic_medical_record = format_basic_medical_record
        self.format_department_single = format_department_single 
        self.format_department_multi = format_department_multi
        self.format_hospital_register = format_hospital_register
        self.format_hospital_register_modify = format_hospital_register_modify
        self.format_diagnose = format_diagnose
        self.format_examine_assay = format_examine_assay
        self.format_prescription = format_prescription
        self.format_transfusion = format_transfusion
        self.format_disposition = format_disposition
        self.format_pick_therapy = format_pick_therapy
        self.format_generate_therapy = format_generate_therapy
        self.format_generate_medicine = format_generate_medicine
        self.format_return_visit = format_return_visit
        self.format_hospital_guide1 = format_hospital_guide1
        self.format_hospital_guide2 = format_hospital_guide2
        self.format_translate = format_translate
        self.format_new_regiter_info = format_new_regiter_info

    def set_prompt(self):
        self.prompt = {}
        return self.prompt

    def get_prompt(self, flag):
        return self.prompt.get(str(flag))

def register_prompt(cls):
    scene, ver = cls.__name__.split("_")
    VersionedPromptFactory[scene][ver] = cls
    return cls

def get_prompt(scene: str, req, *args):
    ver = req.chat.prompt_version
    if ver == "":
        ver = max(VersionedPromptFactory[scene])
        req.chat.prompt_version = ver
    if ver not in VersionedPromptFactory[scene]:
        print(f"Error not found version {ver} fallback to v1", flush=True)
        raise NotImplemented(f"not implement {ver} version in {scene} prompt")
    return VersionedPromptFactory[scene][ver](req, *args)

class PromptManager:
    def __init__(self, yaml_name):
        try:
            self.yaml_name = yaml_name
            prompt_config_path = "./diagnosis_treatment/prompt_config"
            yaml_path = os.path.join(os.getcwd(), prompt_config_path, yaml_name)
            with open(yaml_path, 'r', encoding='utf-8') as f:
                self.data = yaml.safe_load(f)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"YAML file '{yaml_name}' not found in path '{prompt_config_path}'")
        except yaml.YAMLError as e:
            raise HTTPException(status_code=422, detail=f"Error parsing YAML file: {yaml_name}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error loading YAML: {e}")

    def get_prompt(self, category, index, variables):
        try:
            template_str = self.data["prompts"][category][index]['prompt']
            template = Template(template_str)
            return template.render(**variables)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error getting prompt: {e}")