import json
from jsonschema import validate, ValidationError

schema = {
    "type": "object",
    "properties": {
        "Engineer": { "type": "string" },
        "Company": { "type": "string" },
        "Extended Checks": {
            "type": "array",
            "items": { "type": "string" }
        },
        "URL Checks": {
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "url": { "type": "string" },
                            "description": { "type": "string" }
                        },
                        "required": ["url"]
                    }
                }
            },
            "additionalProperties": False
        }
    },
    "required": ["URL Checks"]
}

data = {
    "Engineer": "Paul Smith",
    "Company": "ACME",
    "Extended Checks": ["TLS-VERSIONS", "DNS"],
    "URL Checks": {
        "Search Engines": [
            { "url": "https://google.com", "description": "Google" },
            { "url": "https://bing.com", "description": "Bing" }
        ],
        "News Sites": [
            { "url": "https://www.bbc.co.uk/news/uk", "description": "BBC News" },
            { "url": "https://news.bbc.co.uk/asdasa", "description": "BBC News - OLD" }
        ]
    }
}

try:
    s = open("web-checker-schema.json")
    schema = json.load(s)
    print(schema)
    validate(instance=data, schema=schema)
    print("✅ JSON is valid!")
except ValidationError as e:
    print("❌ JSON is invalid:", e.message)