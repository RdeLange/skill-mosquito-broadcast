## Mosquito Broadcast
Allow Mycroft to broadcast messages to all other mycroft devices having the broadcast skill installed and listening to the same topic on the same mqtt server.

## Description
This skill has three purposes:
1) Broadcast messages to other mycroft devices
2) Receive broadcast messages from other mycroft devices
3) Repeat the last broadcast message which was send to the mqtt topic specified

And a warning: Due to the way this skill is implemented, it may stop working in case of a live update, under certain circumstances. A workaround is restarting the skill (or restarting Mycroft).
The problem only affects this skill. I am still looking for a solution to this.


### Configuration
The skill is configured on your "Mycroft Home" page. Configure the mqtt server, port and topic that the skill will listen for text messages on.
Currently, password or certificates are not supported. (Maybe I will implement it if you promise to test it :)

A restart of the skill is needed when changing the configuration.

Optionally, it is possible to split the text, using a regular expression.

Example CamelCase: If you send the string "KitchenWindow is open",
you want to split KitchenWindow. After the split Mycroft will say "Kitchen Window is open". To do that set the parameters on "Mycroft Home" like this:
* Split text at pattern (optional): [a-z][A-Z]
* Retain characters in matched string until index: 1
* Retain characters in matched string from index: 1

What happens: The regex match "nK" in "KitchenWindow is open". We retain the characters until index 1 of "nK", which is n.
We retain the characters after index 1 of "nK", which is K. And we put a space in the middle.

Example hypen: Convert "Outside-temperature is -5 degrees" to "Outside temperature is -5 degrees"
* Split text at pattern (optional): [a-z|A-Z]-[a-z|A-Z]
* Retain characters in matched string until index: 1
* Retain characters in matched string from index: 2

What happens: The regex match "e-t" in "Outside-temperature is -5 degrees".  We retain the characters until index 1 of "e-t", which is e.
We retain the characters after index 2 of "e-t", which is t. And we put a space in the middle.

Example underscore: Convert "Kitchen_window is open" to "Kitchen Window is open"
* Split text at pattern (optional): _
* Retain characters in matched string until index: 0
* Retain characters in matched string from index: 1

What happens: The regex match "_" in "Kitchen_window is open".  We retain the characters until index 0 of "_", which is no characters.
We retain the characters after index 1 of "_", which is no characters. And we put a space in the middle.


## Example
For this example you must have a mqtt server named "mqttserver". And a configuration on mycroft home setting the server to "mqttserver", port to 1883, and topic to "my-out/text"
Example of broadcast:

* You: "Hey Mycroft, broadcast dinner is ready"
* Mycroft (on your device): "Your message is broadcasted to all other devices"
* Mycroft (on other devices): <DINGDONG> "This is a broadcast message, please pay attention. Dinner is ready"
* You: "Hey Mycroft, last broadcast"
* Mycroft (on your device): "This is a broadcast message, please pay attention. Dinner is ready"

## Installation

The following commands installs the skill manually, replace branch "origin/18.8.1" below with the branch that best corresponds to the mycroft core version you are running:

cd /opt/mycroft/skills/
git clone https://github.com/RdeLange/skill-mosquito-broadcast.git rdelange-mosquito-speak
cd rdelange-mosquito-speak/
git checkout origin/18.8.1

Re-read the "Installation" section of the README.md after checkout, there may be some specifics for the branch you have chosen.

For branch "origin/18.8.1", do the following:

cd <your mycroft-core directory>
# When using bash/zsh use source as shown below, otherwise consult the venv documentation
source .venv/bin/activate
cd /opt/mycroft/skills/rdelange-mosquito-speak/
pip install -r requirements.txt


## Credits
Based on the Mosquito-Speak Skill from Carsten Agerskov (https://github.com/CarstenAgerskov)
