class BaseLLMProvider:
    provider_name = "base"

    def categorize(self, context):
        raise NotImplementedError
