# subnetter
Python script for generating repetitive config files from a JSON description of ip networks.

Originally part of another repository found [here](https://github.com/kradalby/suberduber)

## Usage

| Parameter | Description | Default value |
| --------- | ----------- | ------------- |
| -n/--network  NETWORK | File containing network description in JSON format |  None. Required. |
| -t/--template TEMPLATE | jinja2 template | None. Required. |
| -f, --file | Output each resulting network to a file | None. Optional. |
| -o/--output-dir OUT_DIR | Folder to store files in. Only has effect if -f is passed. | ./output |

### Network description file

The network description file is a JSON file that contain the networks what is used for generating the output.

The base of the file is an array of network descriptions.
Each description must contain a ```network``` and a list of ```subnets```.
Every subnet must specify its ```size``` and ```name```
It can also specify a ```number``` and ```per-row``` parameter that describes how many config files should be generated for that subnet.
Default values for these are 1. The total number of networks per entry is ```number * per-row```.

Example file:
```json
[
    {
        "network" : "192.168.0.0/24",
        "subnets" : [
            {
                "size" : 27,
                "per-row": 1,
                "name": "Deltakerrad",
                "number" : 4
            },
            {
                "size" : 26,
                "name" : "Tech"
            },
            {
                "size" : 26,
                "name" : "Wireless",
                "number" : 1
            }
        ]
    }
]
```

### Template

The templates uses jinja2 syntax.

Available parameters:

| Parameter | Description | Example value |
| --------- | ----------- | ------------- |
| port | Port number. Auto-increments from 1 | 3 |
| name | The name from the JSON file. Appended with a number in case of multiples | Deltakerrad-3 |
| network | Network address | 192.168.0.0 |
| gateway | Gateway address | 192.168.0.1 |
| start | Address after gateway | 192.168.0.2 |
| end | Last assignable address | 192.168.0.254 |
| addresses | List of usable addresses | 192.168.0.1 - 192.168.0.254 |
| broadcast | The broadcast address | 192.168.0.255 |
| netmask | The netmask | 255.255.255.0 |
| size | The network prefix size | 24 |
