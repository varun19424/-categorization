from rest_framework import serializers


class TransactionInputSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=255)
    vendor = serializers.CharField(max_length=255, required=False, allow_blank=True)


class HistoricalTransactionSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=255)
    vendor = serializers.CharField(max_length=255, required=False, allow_blank=True)
    category = serializers.CharField(max_length=255)


class CompanyContextSerializer(serializers.Serializer):
    company_id = serializers.CharField(max_length=100)
    industry = serializers.CharField(max_length=100)
    chart_of_accounts = serializers.ListField(
        child=serializers.CharField(max_length=255),
        allow_empty=True,
    )
    historical_transactions = HistoricalTransactionSerializer(many=True)

    def validate_chart_of_accounts(self, value):
        if not value:
            raise serializers.ValidationError("Chart of accounts cannot be empty")
        return value


class CategorizationRequestSerializer(serializers.Serializer):
    transaction = TransactionInputSerializer()
    company_context = CompanyContextSerializer()


class CategorizationResponseSerializer(serializers.Serializer):
    category = serializers.CharField()
    confidence = serializers.FloatField()
    reasoning = serializers.CharField()
