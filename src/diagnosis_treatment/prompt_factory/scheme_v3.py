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

import json
from ..prompt_template import *
from fastapi import HTTPException

@register_prompt
class PromptScheme_v3(PromptTemplate):
    def __init__(self, receive, scheme, sub_scheme) -> None:
        super().__init__()
        self.yaml_name = "scheme_v3.yaml"
        self.prompt_manager = PromptManager(self.yaml_name)
        self.scheme = scheme
        self.sub_scheme = sub_scheme
        self.ci_p = receive.input.client_info[0].patient
        self.bmr = receive.input.basic_medical_record
        self.diag = receive.input.diagnosis
        #self.diagnose_definite = [(item.diagnosis_name_retrieve or item.diagnosis_name)
        #    for item in self.diag if item.diagnosis_identifier == "确诊"]
        self.diagnose_definite = [(item.diagnosis_name_retrieve or item.diagnosis_name)
            for item in self.diag]
        self.pick_therapy = receive.output.pick_therapy
        physical_examination = json.loads(self.bmr.physical_examination.json())
        self.physical_examination = {reversed_sub_medical_fields.get(k): v for k, v in physical_examination.items()}
        self.output = receive.output

    def set_prompt(self):
        self.variables = {
            "format_pick_therapy": self.format_pick_therapy,
            "patient_name": self.ci_p.patient_name,
            "patient_gender": self.ci_p.patient_gender,
            "patient_age": self.ci_p.patient_age,
            "chief_complaint": self.bmr.chief_complaint,
            "history_of_present_illness": self.bmr.history_of_present_illness,
            "personal_history": self.bmr.personal_history,
            "allergy_history": self.bmr.allergy_history,
            "physical_examination": self.physical_examination,
            "auxiliary_examination": self.bmr.auxiliary_examination,
            "diagnose_definite": self.diagnose_definite,
            "format_generate_therapy": self.format_generate_therapy,
            "format_generate_medicine": self.format_generate_medicine
        }
        self.prompt = {
            "6": self.__set_default_therapy(),
        }
        return self.prompt

    def __therapy_interpret(self, sub_scheme):
        if self.pick_therapy != []:
           therapy_interpret = [i.interpret_therapy for i in self.pick_therapy if i.picked_therapy == sub_scheme]
        else:
           therapy_interpret = ['无']
        return therapy_interpret 

    def __medicine_interpret(self, sub_scheme):
        medicine_interpret = ""
        if getattr(self.output, sub_scheme).method != []:
            for index, value in enumerate(getattr(self.output, sub_scheme).method[0].methodtherapy_content):
                medicine_interpret += f"""{index+1}. {value.method_plan}\n"""
        else:
            medicine_interpret = "无"
        return medicine_interpret

    def __set_default_therapy(self):
        scheme_error = "Invalid Parameter: scheme must be within pick_therapy, generate_therapy, generate_medicine."
        sub_scheme_error = "Invalid Parameter: sub_scheme must be within default_therapy, surgical_therapy, \
chemo_therapy, radiation_therapy, psycho_therapy, rehabilitation_therapy, physical_therapy, alternative_therapy, observation_therapy."
        if self.scheme == "pick_therapy":
            pass
        elif self.scheme == "generate_therapy":
            if self.sub_scheme in therapy_scheme_fields.values():
                self.variables["picked_therapy"] = reversed_therapy_scheme_fields[self.sub_scheme]
                self.variables["therapy_interpret"] = self.__therapy_interpret(self.sub_scheme)
            else:
                raise HTTPException(status_code=400, detail=sub_scheme_error)
        elif self.scheme == "generate_medicine":
            if self.sub_scheme in therapy_scheme_fields.values():
                self.variables["picked_therapy"] = reversed_therapy_scheme_fields[self.sub_scheme]
                self.variables["medicine_interpret"] = self.__medicine_interpret(self.sub_scheme)
            else:
                raise HTTPException(status_code=400, detail=sub_scheme_error)
        else:
            raise HTTPException(status_code=400, detail=scheme_error)
        system_str = self.prompt_manager.get_prompt(self.scheme, 0, self.variables)
        user_str = self.prompt_manager.get_prompt(self.scheme, 1, self.variables)
        return system_str, user_str