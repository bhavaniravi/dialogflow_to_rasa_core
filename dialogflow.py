class Intent:
    def __init__(self, intent_json):
        self.name = intent_json["name"]
        intent_json = intent_json["responses"][0]
        self.entities = [Entity(params) for params in intent_json["parameters"]]
        self.out_context = [OutContext(context) for context in intent_json["affectedContexts"]]
        self.action = intent_json["action"]
        self.responses = Responses(intent_json["messages"])
        # self.user_says = UserSays(self.name)

# class UserSays:
#     def __init__(self,intent_name):


class Entity:
    def __init__(self, entity_json):
        self.name = entity_json["name"]
        self.required = entity_json["required"]
        self.prompts =[prompt["value"] for prompt in entity_json["prompts"]]


class OutContext:
    def __init__(self, context_json):
        self.name = context_json["name"]


class Responses:
    def __init__(self, response_json):
        self.messages = [prompt["speech"] for prompt in response_json]
