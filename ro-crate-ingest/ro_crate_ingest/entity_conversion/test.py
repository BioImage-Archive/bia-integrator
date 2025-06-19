from pydantic import BaseModel, Field

test = {
    "name": "Test Entity",
}

class TestClass(BaseModel):
    name: str = Field(description="Name of the test entity")


obj = TestClass(**test)

print(test["name"])
print(getattr(obj, "name"))