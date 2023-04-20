
import yaml
import os
import json
import subprocess

from scripts.gpt4 import GPT4

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)

gpt4 = GPT4()
gpt4.set_api_key(config['openai']['api_key'])


# Set service name and description
service_name = 'TeamBuilder' # input('Service name: ')
service_description = 'A tool to help you build your team. User can make a team and invite other users. Users can allow or deny the invitation. Users can also leave the team.' # input('Service description: ')

service_name_snake = service_name[0].lower() + ''.join(['_' + c.lower() if c.isupper() else c for c in service_name[1:]])

if not os.path.exists('projects'):
    os.mkdir('projects')

if not os.path.exists(f'projects/{service_name}'):
    os.mkdir(f'projects/{service_name}')

if not os.path.exists(f'projects/{service_name}/blueprint'):
    os.mkdir(f'projects/{service_name}/blueprint')

# Set environment for Next.js
if not os.path.exists(f'projects/{service_name}/nextjs'):
    with open('prompts/environment_setter.txt', 'r') as f:
        environment_setter_prompt = f.read() + f'./projects/{service_name}/nextjs'

    envchat = [
        {
            "role": "system",
            "content": environment_setter_prompt
        },
        {
            "role": "assistant",
            "content": "Let's see what files are here.\n$ls -a"
        },
        {
            "role": "user",
            "content": ".\n..\ncomponents.txt\ndraft.txt\n"
        }
    ]

    while True:
        response = gpt4.chat(envchat)
        command = response['choices'][0]['message']['content']
        print(f"{bcolors.OKGREEN}Assistant: {bcolors.ENDC}", command)
        if '<END>' in command: break
        envchat.append({
            "role": "assistant",
            "content": command
        })
        command = command.split('$')[1]
        result = subprocess.run(command, capture_output=True, shell=True, encoding='utf-8')
        resulttext = result.stdout if result.returncode == 0 else result.stderr
        print(f"{bcolors.OKBLUE}Console: {bcolors.ENDC}", resulttext)
        if len(resulttext) > 1000: resulttext = resulttext[:500] + '\n...\n' + resulttext[-500:] + '\n'
        envchat.append({
            "role": "user",
            "content": resulttext
        })

if not os.path.exists(f'projects/{service_name_snake}/blueprint/draft.txt'):
    with open('prompts/draft_generator.txt', 'r') as f:
        draft_generator_prompt = f.read()

    response_draft = gpt4.chat([
        {
            "role": "system",
            "content": draft_generator_prompt
        },
        {
            "role": "user",
            "content": f"[Application Information]\n- Name: {service_name}\n- Description: {service_description}"
        }
    ])

    with open(f'projects/{service_name_snake}/blueprint/draft.txt', 'w') as f:
        f.write(response_draft['choices'][0]['message']['content'])
    draft = response_draft['choices'][0]['message']['content']
else:
    with open(f'projects/{service_name_snake}/blueprint/draft.txt', 'r') as f:
        draft = f.read()

if not os.path.exists(f'projects/{service_name_snake}/blueprint/components.txt'):
    with open('prompts/component_generator.txt', 'r') as f:
        conmponent_generator_prompt = f.read()

    response_components = gpt4.chat([
        {
            "role": "system",
            "content": conmponent_generator_prompt
        },
        {
            "role": "user",
            "content": response_draft['choices'][0]['message']['content']
        }
    ])

    with open(f'projects/{service_name_snake}/blueprint/components.txt', 'w') as f:
        f.write(response_components['choices'][0]['message']['content'])
    
    components = response_components['choices'][0]['message']['content']
else:
    with open(f'projects/{service_name_snake}/blueprint/components.txt', 'r') as f:
        components = f.read()

components = components.split('\n\n')

for component in components:
    component_name = component.split('\n')[0]
    component_properties = component.split('\n')[1:]
    component_dict = {'name': component_name[1:-1]}
    for property in component_properties:
        if property:
            kvsplit_ind = property.find(': ')
            key = property[:kvsplit_ind].replace('- ', '').replace(' ', '_').lower()
            value = property[kvsplit_ind+2:]

            if key == 'used_in':
                value = value.split(', ')

            component_dict[key] = value
    
    print(component_dict)
