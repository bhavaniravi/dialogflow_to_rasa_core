class Intent:
    def __init__(self, intent_json):
        self.name = intent_json["name"]
        self.entites = Entity(intent_json["parameters"])
        self.input_context = Context(intent_json["affectedContexts"])
        self.action = intent_json["action"]
        self.responses = Responses(intent_json["messages"])
        # self.user_says = UserSays(self.name)

# class UserSays:
#     def __init__(self,intent_name):


class Entity:
    def __init__(self, entity_json):
        self.name = entity_json["name"]
        self.required = entity_json["required"]
        self.prompts =[ prompt["value"] for prompt in entity_json["prompts"]]
        return self


class Context:
    def __init__(self, context_json):
        self.name = context_json["name"]
        return self


class Responses:
    def __init__(self, response_json):
        self.messages = [prompt["speech"] for prompt in response_json["messages"]]
        return self
