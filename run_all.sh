# # Function to run a command in a new terminal
# run_in_new_terminal() {
#   local cmd=$1
#   if [[ "$OSTYPE" == "linux-gnu"* ]]; then
#     gnome-terminal -- bash -c "source ~/.bashrc; conda activate droodle; cd $(pwd); $cmd; exec bash"
#   elif [[ "$OSTYPE" == "darwin"* ]]; then
#     osascript -e "tell application \"Terminal\" to do script \"source ~/.bash_profile; conda activate droodle; cd $(pwd); $cmd\""
#   elif [[ "$OSTYPE" == "msys" ]]; then
#     start cmd.exe /k "source ~/.bashrc && conda activate droodle && cd $(pwd) && $cmd"
#   else
#     echo "Unsupported OS: $OSTYPE"
#     exit 1
#   fi
# }

# # Function to update the config.json file with the appropriate IP address
# update_config() {
#   local ip=$1
#   jq --arg ip "$ip" '.server_ip = $ip' config.json > tmp.$$.json && mv tmp.$$.json config.json
# }

# # Determine the IP address to use
# if [[ "$1" == "pilotC3" ]]; then
#   ip=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
# else
#   ip="localhost"
# fi

# # Update the config.json file
# update_config "$ip"

# # Print the IP address
# echo "Using IP address: $ip"

# # Run the specified pilot script
# if [[ "$1" == "pilotC1" || "$1" == "pilotC2" || "$1" == "pilotC3" ]]; then
#   run_in_new_terminal "cd interfaces && python3 $1.py"
# else
#   echo "Usage: $0 {pilotC1|pilotC2|pilotC3}"
#   exit 1
# fi

# # Run DroodleUI
# run_in_new_terminal "cd DroodleUI/ui && npm run dev"

# # Run MentorUI if pilotC3 is specified
# if [[ "$1" == "pilotC3" ]]; then
#   run_in_new_terminal "cd MentorUI/ui && npm run dev"
# fi


#!/bin/bash

# Function to run a command in a new terminal
run_in_new_terminal() {
  local cmd=$1
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    gnome-terminal -- bash -c "source ~/.bashrc; conda activate droodle; cd $(pwd); $cmd; exec bash"
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell application \"Terminal\" to do script \"source ~/.bash_profile; conda activate droodle; cd $(pwd); $cmd\""
  elif [[ "$OSTYPE" == "msys" ]]; then
    start cmd.exe /k "source ~/.bashrc && conda activate droodle && cd $(pwd) && $cmd"
  else
    echo "Unsupported OS: $OSTYPE"
    exit 1
  fi
}

# Function to update the config.json file with the appropriate IP address
update_config() {
  local ip=$1
  jq --arg ip "$ip" '.server_ip = $ip' config.json > tmp.$$.json && mv tmp.$$.json config.json
}

# Determine the IP address to use
if [[ "$1" == "pilotC3" ]]; then
  if [[ "$2" == "localhost" ]]; then
    ip="localhost"
  else
    ip=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
  fi
else
  ip="localhost"
fi

# Update the config.json file
update_config "$ip"

# Print the IP address
echo "Using IP address: $ip"

# Run the specified pilot script
if [[ "$1" == "pilotC1" || "$1" == "pilotC2" || "$1" == "pilotC3" ]]; then
  run_in_new_terminal "cd interfaces && python3 $1.py"
else
  echo "Usage: $0 {pilotC1|pilotC2|pilotC3} [localhost]"
  exit 1
fi

# Run DroodleUI
run_in_new_terminal "cd DroodleUI/ui && npm run dev"

# Run MentorUI if pilotC3 is specified
if [[ "$1" == "pilotC3" ]]; then
  run_in_new_terminal "cd MentorUI/ui && npm run dev"
fi