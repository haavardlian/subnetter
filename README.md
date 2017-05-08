# subnetter
Python script for generating repetitive config files from a JSON description of networks

## Usage

### Network description file

The network description file is a JSON file that contain the networks what is used for generating the output.

The base of the file is an array of network descriptions.
Each description must contain a network and a list of subnets.
Every subnet must specify its size the name and the number of subnets to generate. It can also specify a per-row
parameter that describes how many config files should be generated for that one subnet.

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
                "number" : 10
            },
            {
                "size" : 26,
                "name" : "Tech",
                "number" : 1
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
| start | Start of address range | 192.168.0.2 |
| start_next | Next address after start | 192.168.0.3 |
| end | The last assignable address | 192.168.0.254 |
| broadcast | The broadcast address | 192.168.0.255 |
| netmask | The netmask | 255.255.255.0 |
| size | The network prefix size | 24 |



