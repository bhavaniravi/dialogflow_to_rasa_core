from rasa_nlu.training_data import load_data
import json
import argparse
import os
import yaml
import copy

from dialogflow import Intent

DOMAIN_FILE = "data/domain.yml"
STORIES_FILE = "data/stories.md"
NLU_TRAINING_FILE = "data/nlu_data.md"



def create_argument_parser():
    """Parse all the command line arguments."""

    parser = argparse.ArgumentParser(
            description='Creates the parser')
    parser.add_argument(
            '-d', '--dialogflow',
            type=str,
            default="dialogflow",
            help="Directory path of the dialogflow files")
    return parser



class dialogflow_convert(object):
    """Class that converts the dialogflow export to RASA 
    file format"""
    def __init__(self, 
                df_directory="dialogflow",
                NLU_training_file="data/nlu_data.md",
                domain_file="data/domain.yml",
                stories_file="data/stories.md"
                ):

        self.df_directory=df_directory
        self.NLU_training_file=NLU_training_file
        self.domain_file=domain_file
        self.stories_file=stories_file


    def construct_interpreter(self,training_data):
        """
        converts and writes training data to markdown
        :param training_data:
        :return: Core-intents file
        """
        with open(self.NLU_training_file, 'w') as outfile:
            outfile.write(training_data.as_markdown())


    def construct_df_intents_to_objects(self):
        """
        Converts all the intents files to list of intent objects
        :param df_directory:
        :return:
        """
        intent_directory = self.df_directory + "/intents/"
        intents = []
        for file in os.listdir(intent_directory):
            if file.endswith("_usersays_en.json") or file.endswith("_usersays_es.json") :
                continue
            with open(intent_directory + file, "r") as f:
                intent_file = json.load(f)
                intent = Intent(intent_file)
                intents.append(intent)
        return intents


    def construct_templates(self,intents):
        """
        Constructs templates from Dialogflow training data
        :param intents:
        :return: actions, templates
        """
        template_list = {}
        action_list = []
        for intent in intents:
            texts = intent.responses.messages
            if isinstance(texts[0],list):
                from itertools import chain
                texts = list(chain.from_iterable(texts))
            template_list.update({intent.action: [{"text": text} for text in texts]})
            action_list.append(intent.action)
            # Slot filling prompts
            for entity in intent.entities:
                if entity.required:
                    action = intent.action + "_without_" + entity.name
                    action_list.append(action)
                    template_list.update({action: [{"text":text} for text in entity.prompts]})

        return action_list, template_list



    def write_domain_file(self,intents, actions, templates):
        with open(self.domain_file, 'w') as outfile:
            yaml.dump({"intents":intents, "actions":actions, "templates": templates}, 
                        outfile, default_flow_style=False)


    def construct_domain(self,intents):
        """
        Construct core domain from intents actions and templates
        Writes a domain.yml file
        :param intents
        """
        intent_list = [intent.name for intent in intents]
        actions, templates = self.construct_templates(intents)
        self.write_domain_file(intent_list, actions, templates)


    def construct_stories_md_string(self,intent):
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
                    final_string += f"\n## {intent.name}_without_{entity.name}\n    * {intent.name}\n        - {action}_without_{entity.name}\n    {slot_str} "

            entity_dict = str(entity_dict) if entity_dict else ""

            return final_string + f"\n## {intent.name}\n    * {intent.name}{entity_dict} \n         - {action}\n    {slot_str}"
        except TypeError as e:
            print (e)
            # Ignore non-intent files"
            return ""

    def construct_stories(self,intents):
        """
        Constructs Core actions from NLU training data
        :param training_data:
        :return: Core-intents file
        """

        md_string = u""
        for intent in intents:
            md_string += self.construct_stories_md_string(intent)
        with open(self.stories_file, 'w') as outfile:
            outfile.write(md_string)


    def construct_rasa_core(self):
        """Driver function to construct domain and 
        stories files"""

        # step --1
        # Loads the training data
        training_data = load_data(self.df_directory)
        # Saves it in a markdown format
        self.construct_interpreter(training_data)

        # Step -2
        # Getting the intents list
        intents = self.construct_df_intents_to_objects()
        # Constructing and saving the domain as a yaml file
        self.construct_domain(intents)

        # step - 3
        self.construct_stories(intents)




# construct_rasa_core("/home/bhavani/apps/mlandds/rasa_nlu/data/examples/WordBot")
if __name__ == '__main__':
        arg_parser = create_argument_parser()
        cmdline_args = arg_parser.parse_args()

        dialogflow = dialogflow_convert(cmdline_args.dialogflow)
        dialogflow.construct_rasa_core()