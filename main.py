
import yaml
from scripts.gpt4 import GPT4
import os
import json

config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)

gpt4 = GPT4()
gpt4.set_api_key(config['openai']['api_key'])

service_name = 'TeamBuilder' # input('Service name: ')
service_description = 'A tool to help you build your team. User can make a team and invite other users. Users can allow or deny the invitation. Users can also leave the team.' # input('Service description: ')

if not os.path.exists('projects'):
    os.mkdir('projects')

if not os.path.exists(f'projects/{service_name}'):
    os.mkdir(f'projects/{service_name}')

if not os.path.exists(f'projects/{service_name}/draft.txt'):
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

    with open(f'projects/{service_name}/draft.txt', 'w') as f:
        f.write(response_draft['choices'][0]['message']['content'])
    draft = response_draft['choices'][0]['message']['content']
else:
    with open(f'projects/{service_name}/draft.txt', 'r') as f:
        draft = f.read()

if not os.path.exists(f'projects/{service_name}/components.txt'):
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

    with open(f'projects/{service_name}/components.txt', 'w') as f:
        f.write(response_components['choices'][0]['message']['content'])
    
    components = response_components['choices'][0]['message']['content']
else:
    with open(f'projects/{service_name}/components.txt', 'r') as f:
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