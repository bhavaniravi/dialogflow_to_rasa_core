from rasa_nlu.training_data import load_data
import json
import os
import yaml
import copy

from dialogflow import Intent

MODEL_DIRECTORY = './projects/default/'
SAMPLE_CONFIG = "sample_configs/config_spacy.yml"


def construct_templates(intents):
    """
    Constructs templates from Dialogflow training data
    :param intents:
    :return: Core-intents file
    """
    template_list = []
    action_list = []
    for intent in intents:
        texts = intent.responses.messages
        template_list.append({"action":intent.action, "text":texts })
        action_list.append(intent.action)
        ## Slot filling prompts
        for entity in intent.entities:
            if entity.required:
                action = intent.action + "_without_" + entity.name
                action_list.append(action)
                template_list.append({"action": action, "text": entity.prompts})
    return action, template_list


def write_domain_file(intents, actions, templates):
    with open('domain.yml', 'w') as outfile:
        yaml.dump({"intents":intents, "actions":actions, "templates": templates}, outfile, default_flow_style=False)


def construct_domain(intents, training_data):
    """
    Construct core domain
    :param intents,
    :param training_data:
    :return:
    """
    intent_list = [intent.name for intent in intents]
    actions, templates = construct_templates(intents)
    write_domain_file(intent_list, actions, templates)


def construct_interpreter(training_data):
    """
    Constructs Core actions from NLU training data
    :param training_data:
    :return: Core-intents file
    """
    with open('nlu_data.md', 'w') as outfile:
        outfile.write(training_data.as_markdown())


def construct_stories_md_string(intent):
    final_string = u""
    try:
        action = intent.action
        entity_dict = {}

        # handling slots
        slot_list = [{context.name:context.name} for context in intent.context_out]
        slot_str = "".join(["slot"+str(slot)+"\n" for slot in slot_list])
        slot_str = "-"+slot_str if slot_str else ""

        # entity required case
        for entity in intent.entities:
            entity_dict[entity.name] = entity.value
            if entity.required:
                final_string += f"\n## {intent.name}_without_{entity.name}\n    * {intent}\n        - {action}_without_{entity.name}\n    {slot_str} "

        entity_dict = str(entity_dict) if entity_dict else ""

        return final_string + f"\n## {intent.name}\n    * {intent}{entity_dict} \n         - {action}\n    {slot_str}"
    except (TypeError) as e:
        print (e)
        # Ignore non-intent files"
        return ""

def construct_stories(intents):
    """
    Constructs Core actions from NLU training data
    :param training_data:
    :return: Core-intents file
    """

    md_string = u""
    for intent in intents:
        md_string += construct_stories_md_string(intent)
    with open('stories.md', 'w') as outfile:
        outfile.write(md_string)


def construct_df_intents_to_objects(df_directory):
    intent_directory = df_directory + "/intents/"
    intents = []
    for file in os.listdir(intent_directory):
        if file.endswith("_usersays_en.json"):
            continue
        with open(intent_directory + file, "r") as f:
            intent_file = json.load(f)
            intent = Intent(intent_file)
            intents.append(intent)
    print (intents)
    return intents


def construct_rasa_core(df_directory):

    #step --1
    training_data = load_data(df_directory)
    dict_training_data = json.loads(training_data.as_json())
    construct_interpreter(training_data)

    # Step -2
    intents = construct_df_intents_to_objects(df_directory)
    construct_domain(intents, dict_training_data)


    # #step - 3
    construct_stories(intents)


construct_rasa_core("/home/bhavani/apps/mlandds/rasa_nlu/data/examples/WordBot")