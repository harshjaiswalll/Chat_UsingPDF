from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
from requests_aws4auth import AWS4Auth
import json
from pypdf import PdfReader

#REAL ESTATE HOST URL
host = '7i5eknycs53e9kp1qlo8.us-west-2.aoss.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.es.amazonaws.com
region = 'us-west-2'
service = 'aoss'
#credentials = boto3.Session().get_credentials()
auth = AWS4Auth("","", region, service)

client = OpenSearch(
     hosts = [{'host': host, 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    pool_maxsize = 20
)

bedrock_client = boto3.client("bedrock-runtime", region_name="us-west-2",
                    aws_access_key_id="",
                    aws_secret_access_key="",)



def read_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if query in page_text:
            text += page_text
            break  # Stop reading after finding the query
    return text

def text_embedding(text):
    body=json.dumps({"inputText": text})
    response = bedrock_client.invoke_model(body=body, modelId='amazon.titan-embed-text-v1', accept='application/json', contentType='application/json')
    response_body = json.loads(response.get('body').read())
    embedding = response_body.get('embedding')
    return embedding

def add_document(vector,text):
    document = {
      "sandbox_vector": vector,
      "sandbox_text": text
    }
    
    response = client.index(
        index = 'sandbox',
        body = document
    )
    print('\nAdding document:')
    print(response)

# path = "1.pdf"
# text = read_pdf(path)
# embedding = text_embedding(text)
# add_document(embedding,text)
#segments = [text[i:i+300] for i in range(0, len(text), 300)]

# Print each segment
# for segment in segments:
#     print("--------------------------------------------------")

#     print(segment)
#     print("--------------------------------------------------")
#     embedding = text_embedding(segment)
#     add_document(embedding,segment)


 



# print(text)
# print(len(embedding))
# document = {
#       "new2_vector": embedding,
#       "new2_text": text
#     }
# response = client.index(
#         index = 'new2',
#         body = document
#     )

# print('\nAdding document:')
# print(response) 

print("SEARCHING START")
query='Tell me about yourself?'
vector=text_embedding(query)
print(len(vector))
document = {
        "size": 50,
        "_source": {"excludes": ["sandbox_vector"]},
        "query": {
            "knn": {
                 "sandbox_vector": {
                     "vector": vector,
                     "k":50
                 }
            }
        }
    }

response = client.search(
    body = document,
    index = "sandbox"
)

print(response)


#################### ADD DOCUMENT
# document = {
#       "new2_vector": embedding,
#       "new2_text": text
#     }
# response = client.index(
#         index = 'new2',
#         body = document
#     )

# print('\nAdding document:')
# print(response) 








##################CREATE INDEX #######################
# index_name = "test_index"
# index_body = {
#     "mappings": {
#         "properties": {
#             "testapp_text": {"type": "text"},
#             "testapp_vector": {
#                 "type": "knn_vector",
#                 "dimension": 4096,
#                 "method": {
#                     "engine": "nmslib",
#                     "space_type": "cosinesimil",
#                     "name": "hnsw",
#                     "parameters": {"ef_construction": 512, "m": 16},
#                 },
#             },
#         }
#     },
#     "settings": {
#         "index": {
#             "number_of_shards": 2,
#             "knn.algo_param": {"ef_search": 512},
#             "knn": True,
#         }
#     },
# }

# try:
#     response = client.indices.create(index_name, body=index_body)
#     print(json.dumps(response, indent=2))
# except Exception as ex:
#     print(ex)