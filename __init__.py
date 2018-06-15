from rasa_nlu.training_data import load_data
from rasa_nlu.training_data.formats.dialogflow import DialogflowReader
import json
import os
import yaml
import copy

MODEL_DIRECTORY = './projects/default/'
SAMPLE_CONFIG = "sample_configs/config_spacy.yml"
DATA_PATH = 'data/examples/rasa/demo-rasa.json'


def construct_intents(training_data):
    """
    Constructs Core intents from NLU training data
    :param training_data:
    :return: Core-intents file
    """
    examples = training_data["rasa_nlu_data"]["common_examples"]
    return list(set([eg["intent"] for eg in examples]))


def construct_templates(df_directory):
    """
    Constructs templates from NLU training data
    :param training_data:
    :return: Core-intents file
    """
    intent_directory = df_directory+"/intents/"
    final_list = []
    for file in os.listdir(intent_directory):
        with open(intent_directory+file,"r") as f:
            intent_file = json.load(f)
            try:
                responses = intent_file["responses"][0]
                texts = responses["messages"][0]["speech"]
                if type(texts) != type([]):
                    texts = [texts]
                final_list.append({"action":responses["action"],
                            "text":texts })
            except TypeError:
                # Ignore non-intent files"
                continue
    return final_list


def write_domain_file(intents, actions, templates):
    with open('domain.yml', 'w') as outfile:
        yaml.dump({"intents":intents, "actions":actions, "templates":templates}, outfile, default_flow_style=False)


def construct_domain(df_directory, training_data):
    """
    Construct core domain
    :param training_data:
    :return:
    """
    intents = construct_intents(training_data)
    templates = construct_templates(df_directory)
    actions = copy.deepcopy(intents)
    write_domain_file(intents, actions, templates)


def construct_interpreter(training_data):
    """
    Constructs Core actions from NLU training data
    :param training_data:
    :return: Core-intents file
    """
    with open('nlu_data.md', 'w') as outfile:
        outfile.write(training_data.as_markdown())


def construct_stories(df_directory):
    """
    Constructs Core actions from NLU training data
    :param training_data:
    :return: Core-intents file
    """

    md_string = u""
    intent_directory = df_directory + "/intents/"
    for file in os.listdir(intent_directory):
        with open(intent_directory + file, "r") as f:
            intent_file = json.load(f)
            try:
                intent = story_title = intent_file["name"]
                responses = intent_file["responses"][0]
                action = responses["action"]
            except TypeError:
                # Ignore non-intent files"
                continue
        md_string += f"\n## {story_title}\n     * {intent} \n       - {action} "

    with open('stories.md', 'w') as outfile:
        outfile.write(md_string)



def construct_rasa_core(df_directory):

    # step --1
    training_data = load_data(df_directory)
    dict_training_data = json.loads(training_data.as_json())
    construct_domain(df_directory, dict_training_data)

    # # Step -2
    construct_interpreter(training_data)
    #
    # #step - 3
    construct_stories(df_directory)


construct_rasa_core("/home/bhavani/apps/mlandds/rasa_nlu/data/examples/WordBot")