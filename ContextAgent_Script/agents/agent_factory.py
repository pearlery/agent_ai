import json
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.callbacks import StdOutCallbackHandler
from config.Config import cfg
from tools.Example_Log_Keeper import example_log_body2 as example_log
from tools.Example_Log_Keeper import example_type_body2 as example_type
from tools.escape_prompt_braces import load_escaped_prompt_template
#from tools.Example_Log_Keeper import example_client_tools_body as example_client_tools

class AgentFactory:
    def __init__(self):
        self.config = cfg
        handler = StdOutCallbackHandler()
        self.llm = OllamaLLM(
            model=self.config.LLM_MODEL,
            temperature=self.config.LLM_TEMPERATURE,
            callbacks=[handler],
            base_url=self.config.LOCAL_LLM_URL
        )
        print("⚙️ Using LLM_MODEL:", self.config.LLM_MODEL)

    def create_cybersecurity_answer_agent(self):
            """
            Returns a chain that answers cybersecurity questions intelligently.
            The LLM is instructed to only respond if it is confident.
            """

            prompt_template = PromptTemplate(
                input_variables=["question"],
                template=(
                    "You are a cybersecurity expert AI.\n"
                    "Your task is to answer the following question as accurately as possible.\n"
                    "Only answer if you are confident. If you do not know the answer, say 'I'm not sure about that.'\n\n"
                    "Question: {question}\n\n"
                    "Answer:"
                )
            )

            chain = LLMChain(
                llm=self.llm,
                prompt=prompt_template,
                verbose=True
            )

            return chain
        
    
    def create_recommending_agent(self):
        """
        Agent that returns a recommendation based on log, MITRE ATT&CK prediction, and client tools.
        Uses fallback examples if input not provided.
        """
        prompt_template = load_escaped_prompt_template("tools/Recommendation_formated.txt")

        prompt = PromptTemplate(
            input_variables=["log", "mitre_attack_type", "client_tools_json"],
            template=prompt_template
        )

        chain = LLMChain(llm=self.llm, prompt=prompt, verbose=True)

        def run(
            log: dict = example_log["node"],
            mitre_attack_type: dict = example_type,
            client_tools_json: dict = None,
        ) -> str:
            return chain.run({
                "log": json.dumps(log, indent=2),
                "mitre_attack_type": json.dumps(mitre_attack_type, indent=2),
                "client_tools_json": json.dumps(client_tools_json, indent=2),
            })

        return run



#The code after this is used for the nats recieving function

# Initialize the agent only once at startup

from contexts.compose_tools_data import compose_full_tools_data_from_log
from typing import Dict, Any

agent_factory = AgentFactory()
recommendation_agent = agent_factory.create_recommending_agent()

# Function that will reuse the already created agent
async def call_recommendation_agent_from_script(input_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        #print(input_data)
        # Validate or use fallback examples
        log_data = input_data.get("log", {}).get("node")  # or example_log["node"]
        type_data = input_data.get("type")  # or example_type

        # Wrap as Pydantic if needed, or keep as dict
        tools_data = await compose_full_tools_data_from_log({"node": log_data})

        # Reuse the recommendation agent created at startup
        response = recommendation_agent(
            log=log_data,
            mitre_attack_type=type_data,
            client_tools_json=tools_data
        )
        return {"status": "success", "result": response}

    except Exception as e:
        return {"status": "error", "detail": str(e)}

    # def create_recommending_agent(self):
    #     """
    #     Agent that returns a recommendation based on log, MITRE ATT&CK prediction, and client tools.
    #     Uses fallback examples if input not provided.
    #     """
    #     with open("tools/Recommend_with_Context_Template.txt", "r") as f:
    #         prompt_template = f.read()

    #     prompt = PromptTemplate(
    #         input_variables=["log", "mitre_attack_type", "client_tools_json"],
    #         template=prompt_template
    #     )
        
    #     chain = LLMChain(llm=self.llm, prompt=prompt, verbose=True)

    #     def run(
    #         log: dict = example_log["node"],
    #         mitre_attack_type: dict = example_type,
    #         client_tools_json: dict = None,
    #     ) -> str:
    #         return chain.run({
    #             "log": json.dumps(log, indent=2),
    #             "mitre_attack_type": json.dumps(mitre_attack_type, indent=2),
    #             "client_tools_json": json.dumps(client_tools_json, indent=2),
    #         })

    #     return run
