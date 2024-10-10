import os
import json
import random
import argparse
from utils.agent import Agent
from datetime import datetime
from tqdm import tqdm

class DroodleDebate:
    def __init__(self,
                 model_name: str = 'gpt-4o',  # Updated to GPT-4 Vision
                 temperature: float = 0.7,
                 num_players: int = 3,
                 save_file_dir: str = None,
                 openai_api_key: str = None,
                 prompts_path: str = None,
                 max_round: int = 3,
                 sleep_time: float = 0
                 ) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.num_players = num_players
        self.save_file_dir = save_file_dir
        self.openai_api_key = openai_api_key
        self.max_round = max_round
        self.sleep_time = sleep_time

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H:%M:%S")
        self.save_file = {
            'start_time': current_time,
            'end_time': '',
            'model_name': model_name,
            'temperature': temperature,
            'num_players': num_players,
            'success': False,
            "droodle": "",
            'base_title1': '',
            'base_title2': '',
            "debate_result": '',
            "Reason": '',
            "Supported Side": '',
            'players': {},
        }
        prompts = json.load(open(prompts_path))
        self.save_file.update(prompts)
        self.init_prompt()

        self.create_agents()
        self.init_agents()

    def init_prompt(self):
        def prompt_replace(key):
            self.save_file[key] = self.save_file[key].replace("##droodle##", self.save_file["droodle"])
        prompt_replace("title_prompt")
        prompt_replace("agent_meta_prompt")
        prompt_replace("moderator_meta_prompt")
        prompt_replace("judge_prompt_last2")

    def create_agents(self):
        self.players = [
            Agent(model_name=self.model_name, name=name, temperature=self.temperature, openai_api_key=self.openai_api_key, sleep_time=self.sleep_time) for name in ["Agent 1", "Agent 2", "Moderator"]
        ]
        self.agent1 = self.players[0]
        self.agent2 = self.players[1]
        self.moderator = self.players[2]

    def init_agents(self):
        self.agent1.set_meta_prompt(self.save_file['agent_meta_prompt'])
        self.agent2.set_meta_prompt(self.save_file['agent_meta_prompt'])
        self.moderator.set_meta_prompt(self.save_file['moderator_meta_prompt'])
        
        print(f"===== Title Generation Round-1 =====\n")
        self.agent1.add_event(self.save_file['title_prompt'])
        self.title1 = self.agent1.ask(image=open(self.save_file['droodle'], 'rb').read())
        self.agent1.add_memory(self.title1)
        self.save_file['base_title1'] = self.title1

        self.agent2.add_event(self.save_file['title_prompt'])
        self.title2 = self.agent2.ask(image=open(self.save_file['droodle'], 'rb').read())
        self.agent2.add_memory(self.title2)
        self.save_file['base_title2'] = self.title2

        self.moderator.add_event(self.save_file['moderator_prompt'].replace('##title1##', self.title1).replace('##title2##', self.title2).replace('##round##', 'first'))
        self.mod_ans = self.moderator.ask()
        self.moderator.add_memory(self.mod_ans)
        self.mod_ans = eval(self.mod_ans)

    def run(self):
        for round in range(self.max_round - 1):
            if self.mod_ans["debate_result"] != '':
                break
            else:
                print(f"===== Title Refinement Round-{round+2} =====\n")
                self.agent1.add_event(self.save_file['debate_prompt'].replace('##oppo_title##', self.title2))
                self.title1 = self.agent1.ask()
                self.agent1.add_memory(self.title1)

                self.agent2.add_event(self.save_file['debate_prompt'].replace('##oppo_title##', self.title1))
                self.title2 = self.agent2.ask()
                self.agent2.add_memory(self.title2)

                self.moderator.add_event(self.save_file['moderator_prompt'].replace('##title1##', self.title1).replace('##title2##', self.title2).replace('##round##', self.round_dct(round+2)))
                self.mod_ans = self.moderator.ask()
                self.moderator.add_memory(self.mod_ans)
                self.mod_ans = eval(self.mod_ans)

        if self.mod_ans["debate_result"] != '':
            self.save_file.update(self.mod_ans)
            self.save_file['success'] = True

        else:
            judge_player = Agent(model_name=self.model_name, name='Judge', temperature=self.temperature, openai_api_key=self.openai_api_key, sleep_time=self.sleep_time)
            title1 = self.agent1.memory_lst[2]['content']
            title2 = self.agent2.memory_lst[2]['content']

            judge_player.set_meta_prompt(self.save_file['moderator_meta_prompt'])

            judge_player.add_event(self.save_file['judge_prompt_last1'].replace('##title1##', title1).replace('##title2##', title2))
            ans = judge_player.ask()
            judge_player.add_memory(ans)

            judge_player.add_event(self.save_file['judge_prompt_last2'])
            ans = judge_player.ask()
            judge_player.add_memory(ans)
            ans = eval(ans)
            if ans["debate_result"] != '':
                self.save_file['success'] = True
            self.save_file.update(ans)
            self.players.append(judge_player)

        for player in self.players:
            self.save_file['players'][player.name] = player.memory_lst

def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "–input-file", type=str, required=True, help="Input file path")
    parser.add_argument("-o", "–output-dir", type=str, required=True, help="Output file dir")
    parser.add_argument("-k", "–api-key", type=str, required=True, help="OpenAI api key")
    parser.add_argument("-m"," –model-name", type=str, default="gpt-4o", help="Model name")
    parser.add_argument("-t", "–temperature", type=float, default=0.7, help="Sampling temperature")
    return parser.parse_args()

if __name__ == "main":
    args = parse_args()
    openai_api_key = args.api_key

    current_script_path = os.path.abspath(__file__)
    MAD_path = current_script_path.rsplit("/", 2)[0]

    config = json.load(open(f"{MAD_path}/code/utils/config4droodle.json", "r"))

    inputs = open(args.input_file, "r").readlines()
    inputs = [l.strip() for l in inputs]

    save_file_dir = args.output_dir
    if not os.path.exists(save_file_dir):
        os.mkdir(save_file_dir)

    for id, input in enumerate(tqdm(inputs)):
        prompts_path = f"{save_file_dir}/{id}-config.json"
        config['droodle'] = input

        with open(prompts_path, 'w') as file:
            json.dump(config, file, ensure_ascii=False, indent=4)

        debate = DroodleDebate(save_file_dir=save_file_dir, num_players=3, openai_api_key=openai_api_key, prompts_path=prompts_path, temperature=args.temperature, sleep_time=0)
        debate.run()
        debate.save_file_to_json(id)
