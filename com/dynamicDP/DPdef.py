import boto3

client = boto3.client('datapipeline')

# response = client.get_pipeline_definition(
#     pipelineId='df-0326999WA5R5F9K1N0P'
# )

# response = client.describe_pipelines(
#     pipelineIds=['df-0326999WA5R5F9K1N0P']
# )


response = client.describe_objects(
    pipelineId='df-0326999WA5R5F9K1N0P',
    objectIds=[
        'EmrClusterId_lMdQq'
    ])

print (response)