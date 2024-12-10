import json
import os
from openai import AzureOpenAI
import pandas as pd
import requests

from common import check_nan,text_to_base64
from load_azd_env import load_azd_env


# create datasource

def create_datasource(datasource_name:str, connection_string:str, ai_search_endpoint:str, ai_search_key:str, container_name:str):
    print("Creating datasource")

    datasource_payload = {
    "name": datasource_name,
    "description": "Demo files to demonstrate cognitive search capabilities.",
    "type": "adlsgen2",
    "credentials": {
        "connectionString": connection_string
    },
    "container": {
        "name": container_name
    }
}
    headers = {'Content-Type': 'application/json', 'api-key': ai_search_key}
    params = {'api-version': '2024-07-01'}


    r = requests.put(ai_search_endpoint + "/datasources/" + datasource_name,
                    data=json.dumps(datasource_payload), headers=headers, params=params)
    print("status code: ", r.status_code)
    # status check
    if 200 <= r.status_code < 300:
        print("Datasource created successfully")
    else:
        print("Error creating datasource")
    
def create_index(index_name:str, ai_search_endpoint:str, ai_search_key:str, azure_openai_endpoint:str,azure_openai_key:str, text_embedding_model:str):
    print("Creating index")

    index_payload = {
    "name": index_name,
    "fields": [
        {"name": "chunk_id", "type": "Edm.String", "key": "true", "searchable": "true", "analyzer": "keyword", "retrievable": "true", "sortable": "true", "filterable": "true","facetable": "true"},
        {"name": "parent_id", "type": "Edm.String", "searchable": "true", "retrievable": "true", "sortable": "true", "filterable": "true","facetable": "true"},
        {"name": "title", "type": "Edm.String", "searchable": "true", "analyzer": "ja.lucene","retrievable": "true", "facetable": "false", "filterable": "true", "sortable": "false"},
        {"name": "chunk", "type": "Edm.String", "searchable": "true", "analyzer": "ja.lucene","retrievable": "true", "facetable": "false", "filterable": "false", "sortable": "false"},
        {"name": "location", "type": "Edm.String", "searchable": "true", "retrievable": "true", "sortable": "false", "filterable": "false", "facetable": "false"},
        {"name": "language", "type": "Edm.String", "searchable": "true", "retrievable": "true", "sortable": "false", "filterable": "false", "facetable": "false"},
        {"name": "persons", "type": "Collection(Edm.String)", "searchable": "true", "analyzer": "ja.lucene", "retrievable": "true", "sortable": "false", "filterable": "false", "facetable": "false"},
        {"name": "urls", "type": "Collection(Edm.String)", "searchable": "true", "retrievable": "true", "sortable": "false", "filterable": "false", "facetable": "false"},
        {"name": "emails", "type": "Collection(Edm.String)", "searchable": "true", "retrievable": "true", "sortable": "false", "filterable": "false", "facetable": "false"},
        {"name": "key_phrases", "type": "Collection(Edm.String)", "searchable": "true", "analyzer": "ja.lucene", "retrievable": "true", "sortable": "false", "filterable": "false", "facetable": "false"},
        {"name": "original_chunk", "type": "Edm.String", "searchable": "false", "retrievable": "true", "facetable": "false", "filterable": "false", "sortable": "false"},
        {"name": "metadata_storage_path", "type": "Edm.String", "searchable": "false", "retrievable": "true", "facetable": "false", "filterable": "false", "sortable": "false"},
        {"name": "vector","type": "Collection(Edm.Single)", "searchable": "true", "retrievable": "true", "sortable": "false", "filterable": "false", "facetable": "false", "dimensions": 3072, "vectorSearchProfile": "vector-profile"},
    ],
    "semantic": {
      "configurations": [
        {
          "name": "semantic-config",
          "prioritizedFields": {
            "titleField": 
                {
                    "fieldName": "title"
                },
            "prioritizedContentFields": [
                {
                    "fieldName": "chunk"
                }
                ]
          }
        }
      ]
    },
    "vectorSearch": {
      "algorithms": [
        {
          "name": "vector-algorithm",
          "kind": "hnsw",
          "hnswParameters": {
            "metric": "cosine",
            "m": 4,
            "efConstruction": 400,
            "efSearch": 500
          },
          "exhaustiveKnnParameters": None
        }
      ],
      "profiles": [
        {
          "name": "vector-profile",
          "algorithm": "vector-algorithm",
          "vectorizer": "vector-vectorizer",
          "compression": None
        }
      ],
      "vectorizers": [
        {
          "name": "vector-vectorizer",
          "kind": "azureOpenAI",
          "azureOpenAIParameters": {
            "resourceUri": azure_openai_endpoint,
            "deploymentId": 'embedding',
            "apiKey": azure_openai_key,
            "modelName": text_embedding_model,
            "authIdentity": None
          },
          "customWebApiParameters": None,
        }
      ],
      "compressions": []
    }
}
    headers = {'Content-Type': 'application/json', 'api-key': ai_search_key}
    params = {'api-version': '2024-07-01'}

    r = requests.put(ai_search_endpoint + "/indexes/" + index_name,
                    data=json.dumps(index_payload), headers=headers, params=params)
    print("status_code:", r.status_code)
    # status check
    if 200 <= r.status_code < 300:
        print("Index created successfully")
    else:
        print("Error creating index")

def create_skillset(skillset_name:str,index_name:str,ai_search_endpoint:str,ai_search_key:str, azure_openai_endpoint:str, azure_openai_key:str, text_embedding_model:str, aiservices_key:str):
    skillset_payload = {
    "name": skillset_name,
    "description": "Skillset to chunk documents and generate embeddings",
    "skills": [
      {
        "@odata.type": "#Microsoft.Skills.Text.LanguageDetectionSkill",
        "name": "#1.LanguageDetectionSkill",
        "description": "If you have multilingual content, adding a language code is useful for filtering",
        "context": "/document",
        "defaultCountryHint": None,
        "modelVersion": None,
        "inputs": [
          {
            "name": "text",
            "source": "/document/content"
          }
        ],
        "outputs": [
          {
            "name": "languageCode",
            "targetName": "language"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Vision.OcrSkill",
        "name": "#2.OcrSkill",
        "description": None,
        "context": "/document/normalized_images/*",
        "textExtractionAlgorithm": None,
        "lineEnding": "Space",
        "defaultLanguageCode": "ja",
        "detectOrientation": True,
        "inputs": [
          {
            "name": "image",
            "source": "/document/normalized_images/*"
          }
        ],
        "outputs": [
          {
            "name": "text",
            "targetName": "text_from_ocr"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Text.MergeSkill",
        "name": "#3.1.MergeSkillnotforPDF",
        "description": None,
        "context": "/document",
        "insertPreTag": " ",
        "insertPostTag": " ",
        "inputs": [
          {
            "name": "text",
            "source": "/document/content"
          },
          {
            "name": "itemsToInsert",
            "source": "/document/normalized_images/*/text_from_ocr"
          },
          {
            "name": "offsets",
            "source": "/document/normalized_images/*/contentOffset"
          }
        ],
        "outputs": [
          {
            "name": "mergedText",
            "targetName": "merged_text_others"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Text.MergeSkill",
        "name": "#3.2.MergeSkillForPDF",
        "description": None,
        "context": "/document",
        "insertPreTag": " ",
        "insertPostTag": " ",
        "inputs": [
          {
            "name": "itemsToInsert",
            "source": "/document/normalized_images/*/text_from_ocr"
          }
        ],
        "outputs": [
          {
            "name": "mergedText",
            "targetName": "merged_text_pdf"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Util.ConditionalSkill",
        "name": "#3.3.MergeGoal",
        "description": "",
        "context": "/document",
        "inputs": [
          {
            "name": "condition",
            "source": "= $(/document/metadata_content_type)=='application/pdf'"
          },
          {
            "name": "whenTrue",
            "source": "/document/merged_text_pdf"
          },
          {
            "name": "whenFalse",
            "source": "/document/merged_text_others"
          }
        ],
        "outputs": [
          {
            "name": "output",
            "targetName": "merged_text"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Util.ConditionalSkill",
        "name": "#4.1.splitForEnglish",
        "description": "",
        "context": "/document",
        "inputs": [
          {
            "name": "condition",
            "source": "= $(/document/language) == 'ja'"
          },
          {
            "name": "whenTrue",
            "source": "= null"
          },
          {
            "name": "whenFalse",
            "source": "/document/merged_text"
          }
        ],
        "outputs": [
          {
            "name": "output",
            "targetName": "content_not_ja"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Text.SplitSkill",
        "name": "#4.2.SplitSkillfromEnglish",
        "description": "Split skill to chunk documents",
        "context": "/document",
        "defaultLanguageCode": "ja",
        "textSplitMode": "pages",
        "maximumPageLength": 2000,
        "pageOverlapLength": 500,
        "maximumPagesToTake": 0,
        "inputs": [
          {
            "name": "text",
            "source": "/document/content_not_ja"
          },
          {
            "name": "languageCode",
            "source": "/document/language"
          }
        ],
        "outputs": [
          {
            "name": "textItems",
            "targetName": "original_chunks_not_ja"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Util.ConditionalSkill",
        "name": "#4.3.splitForJapanese",
        "description": "",
        "context": "/document",
        "inputs": [
          {
            "name": "condition",
            "source": "= $(/document/language) == 'ja'"
          },
          {
            "name": "whenTrue",
            "source": "/document/merged_text"
          },
          {
            "name": "whenFalse",
            "source": "= null"
          }
        ],
        "outputs": [
          {
            "name": "output",
            "targetName": "content_ja"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Text.SplitSkill",
        "name": "#4.4.SplitSkillfromJapanese",
        "description": "Split skill to chunk documents",
        "context": "/document",
        "defaultLanguageCode": "ja",
        "textSplitMode": "pages",
        "maximumPageLength": 2000,
        "pageOverlapLength": 500,
        "maximumPagesToTake": 0,
        "inputs": [
          {
            "name": "text",
            "source": "/document/content_ja"
          },
          {
            "name": "languageCode",
            "source": "/document/language"
          }
        ],
        "outputs": [
          {
            "name": "textItems",
            "targetName": "original_chunks_ja"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Util.ConditionalSkill",
        "name": "#4.5.merge",
        "description": "",
        "context": "/document",
        "inputs": [
          {
            "name": "condition",
            "source": "= $(/document/language) == 'ja'"
          },
          {
            "name": "whenTrue",
            "source": "/document/original_chunks_ja"
          },
          {
            "name": "whenFalse",
            "source": "/document/original_chunks_not_ja"
          }
        ],
        "outputs": [
          {
            "name": "output",
            "targetName": "original_chunks"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Text.LanguageDetectionSkill",
        "name": "#5.LanguageDetectionSkill_by_chunk",
        "description": "If you have multilingual content, adding a language code is useful for filtering",
        "context": "/document/original_chunks/*",
        "defaultCountryHint": None,
        "modelVersion": None,
        "inputs": [
          {
            "name": "text",
            "source": "/document/original_chunks/*"
          }
        ],
        "outputs": [
          {
            "name": "languageCode",
            "targetName": "chunk_language"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Util.ConditionalSkill",
        "name": "#6.GetNoneJapaneseContent",
        "description": "",
        "context": "/document/original_chunks/*",
        "inputs": [
          {
            "name": "condition",
            "source": "= $(/document/original_chunks/*/chunk_language) == 'ja'"
          },
          {
            "name": "whenTrue",
            "source": "= null"
          },
          {
            "name": "whenFalse",
            "source": "/document/original_chunks/*"
          }
        ],
        "outputs": [
          {
            "name": "output",
            "targetName": "content_not_ja"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Text.TranslationSkill",
        "name": "#7.translateToJapanese",
        "description": "",
        "context": "/document/original_chunks/*",
        "defaultFromLanguageCode": "en",
        "defaultToLanguageCode": "ja",
        "suggestedFrom": "en",
        "inputs": [
          {
            "name": "fromLanguageCode",
            "source": "/document/original_chunks/*/chunk_language"
          },
          {
            "name": "text",
            "source": "/document/original_chunks/*/content_not_ja"
          }
        ],
        "outputs": [
          {
            "name": "translatedText",
            "targetName": "chunk_ja"
          },
          {
            "name": "translatedToLanguageCode",
            "targetName": "translatedToLanguageCode"
          },
          {
            "name": "translatedFromLanguageCode",
            "targetName": "translatedFromLanguageCode"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Util.ConditionalSkill",
        "name": "#8.generateJapanaseChunk",
        "description": "",
        "context": "/document/original_chunks/*",
        "inputs": [
          {
            "name": "condition",
            "source": "= $(/document/original_chunks/*/chunk_language) == 'ja'"
          },
          {
            "name": "whenTrue",
            "source": "/document/original_chunks/*"
          },
          {
            "name": "whenFalse",
            "source": "/document/original_chunks/*/chunk_ja"
          }
        ],
        "outputs": [
          {
            "name": "output",
            "targetName": "chunk"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Text.V3.EntityRecognitionSkill",
        "name": "#9.1.EntityRecognitionSkill",
        "description": None,
        "context": "/document/original_chunks/*",
        "categories": [
          "Person",
          "URL",
          "Email"
        ],
        "defaultLanguageCode": "ja",
        "minimumPrecision": 0.5,
        "modelVersion": None,
        "inputs": [
          {
            "name": "text",
            "source": "/document/original_chunks/*/chunk"
          }
        ],
        "outputs": [
          {
            "name": "persons",
            "targetName": "persons"
          },
          {
            "name": "urls",
            "targetName": "urls"
          },
          {
            "name": "emails",
            "targetName": "emails"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Text.KeyPhraseExtractionSkill",
        "name": "#9.2.KeyPhraseExtractionSkill",
        "description": "",
        "context": "/document/original_chunks/*",
        "defaultLanguageCode": "ja",
        "maxKeyPhraseCount": None,
        "modelVersion": "",
        "inputs": [
          {
            "name": "text",
            "source": "/document/original_chunks/*/chunk"
          }
        ],
        "outputs": [
          {
            "name": "keyPhrases",
            "targetName": "key_phrases"
          }
        ]
      },
      {
        "@odata.type": "#Microsoft.Skills.Text.AzureOpenAIEmbeddingSkill",
        "name": "#9.3.embedding",
        "description": None,
        "context": "/document/original_chunks/*",
        "resourceUri": azure_openai_endpoint,
        "apiKey": azure_openai_key,
        "deploymentId": 'embedding',
        "dimensions": 3072,
        "modelName": text_embedding_model,
        "inputs": [
          {
            "name": "text",
            "source": "/document/original_chunks/*/chunk"
          }
        ],
        "outputs": [
          {
            "name": "embedding",
            "targetName": "vector"
          }
        ],
        "authIdentity": None
      }
    ],
    "cognitiveServices": {
      "@odata.type": "#Microsoft.Azure.Search.CognitiveServicesByKey",
      "description": None,
      "key": aiservices_key
    },
    "knowledgeStore": None,
    "indexProjections": {
      "selectors": [
        {
          "targetIndexName": index_name,
          "parentKeyFieldName": "parent_id",
          "sourceContext": "/document/original_chunks/*",
          "mappings": [
            {
              "name": "title",
              "source": "/document/title",
              "sourceContext": None,
              "inputs": []
            },
            {
              "name": "location",
              "source": "/document/metadata_storage_path",
              "sourceContext": None,
              "inputs": []
            },
            {
              "name": "original_chunk",
              "source": "/document/original_chunks/*",
              "sourceContext": None,
              "inputs": []
            },
            {
              "name": "chunk",
              "source": "/document/original_chunks/*/chunk",
              "sourceContext": None,
              "inputs": []
            },
            {
              "name": "vector",
              "source": "/document/original_chunks/*/vector",
              "sourceContext": None,
              "inputs": []
            },
            {
              "name": "language",
              "source": "/document/original_chunks/*/chunk_language",
              "sourceContext": None,
              "inputs": []
            },
            {
              "name": "persons",
              "source": "/document/original_chunks/*/persons",
              "sourceContext": None,
              "inputs": []
            },
            {
              "name": "urls",
              "source": "/document/original_chunks/*/urls",
              "sourceContext": None,
              "inputs": []
            },
            {
              "name": "emails",
              "source": "/document/original_chunks/*/emails",
              "sourceContext": None,
              "inputs": []
            },
            {
              "name": "key_phrases",
              "source": "/document/original_chunks/*/key_phrases",
              "sourceContext": None,
              "inputs": []
            },
            {
              "name": "metadata_storage_path",
              "source": "/document/metadata_storage_path",
              "sourceContext": None,
              "inputs": []
            }
          ]
        }
      ],
      "parameters": {
        "projectionMode": "skipIndexingParentDocuments"
      }
    },
    "encryptionKey": None

}
    headers = {'Content-Type': 'application/json', 'api-key': ai_search_key}
    params = {'api-version': '2024-07-01'}

    r = requests.put(ai_search_endpoint + "/skillsets/" + skillset_name,
                    data=json.dumps(skillset_payload), headers=headers, params=params)
    print("status code: ", r.status_code)
    # status check
    if 200 <= r.status_code < 300:
        print("Skillset created successfully")
    else:
        print("Error creating skillset")

def create_indexer(indexer_name:str, datasource_name:str, skillset_name:str, index_name:str, ai_search_endpoint:str, ai_search_key:str):
    print("Creating indexer")
    
    indexer_payload = {
        "name": indexer_name,
        "dataSourceName": datasource_name,
        "targetIndexName": index_name,
        "skillsetName": skillset_name,
        # "schedule" : { "interval" : "PT2H"}, # How often do you want to check for new content in the data source
        "disabled": None,
        "schedule": None,
        "parameters": {
            "batchSize": None,
            "maxFailedItems": None,
            "maxFailedItemsPerBatch": None,
            "base64EncodeKeys": None,
            "configuration": {
            "dataToExtract": "contentAndMetadata",
            "parsingMode": "default",
            "excludedFileNameExtensions": "",
            "imageAction": "generateNormalizedImagePerPage",
            "allowSkillsetToReadFileData": True
            }
        },
        "fieldMappings": [
            {
            "sourceFieldName": "metadata_storage_name",
            "targetFieldName": "title",
            "mappingFunction": None
            }
        ],
        "outputFieldMappings": [],
        "encryptionKey": None
    }

    headers = {'Content-Type': 'application/json', 'api-key': ai_search_key}
    params = {'api-version': '2024-07-01'}

    r = requests.put(ai_search_endpoint + "/indexers/" + indexer_name,
                    data=json.dumps(indexer_payload), headers=headers, params=params)
    print("status code: ", r.status_code)
    # status check
    if 200 <= r.status_code < 300:
        print("Indexer created successfully")
    else:
        print("Error creating indexer")
            
if __name__ == "__main__":
    # Load environment variables
    load_azd_env()

    # Get environment variables
    AZURE_SEARCH_KEY = os.getenv('AZURE_SEARCH_KEY')
    AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
    BLOB_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    BLOB_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
    DATASOURCE_NAME = os.getenv('DATASOURCE_NAME', 'test-datasource')
    INDEX_NAME = os.getenv('INDEX_NAME', 'test-index')
    AOAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AOAI_KEY = os.getenv('AZURE_OPENAI_KEY')
    TEXT_EMBEDDING_MODEL = os.getenv('AZURE_OPENAI_EMBEDDING_MODEL')
    AZURE_AISERVICES_KEY = os.getenv('AZURE_AISERVICES_KEY')
    SKILL_SET_NAME = os.getenv('SKILL_SET_NAME', 'test-skillset')
    INDEXER_NAME = os.getenv('INDEXER_NAME', 'test-indexer')
    IS_DATASOURCE_SETUP = os.getenv('IS_DATASOURCE_SETUP', "false")
    IS_DOC_INDEX_SETUP = os.getenv('IS_DOC_INDEX_SETUP', "false")
    IS_INDEXER_SETUP = os.getenv('IS_INDEXER_SETUP', "false")
    IS_SKILLSET_SETUP = os.getenv('IS_SKILLSET_SETUP', "false")
    

    # Call the create_datasource function with the environment variables
    if IS_DATASOURCE_SETUP == "false":
        create_datasource(
            datasource_name=DATASOURCE_NAME,
            connection_string=BLOB_CONNECTION_STRING,
            ai_search_endpoint=AZURE_SEARCH_ENDPOINT,
            ai_search_key=AZURE_SEARCH_KEY,
            container_name=BLOB_CONTAINER_NAME
        )
    else:
        print("Datasource already created. Skipping...")

    # call the create_index function with the environment variables
    if IS_DOC_INDEX_SETUP == "false":
        create_index(
            index_name=INDEX_NAME,
            ai_search_endpoint=AZURE_SEARCH_ENDPOINT,
            ai_search_key=AZURE_SEARCH_KEY,
            azure_openai_endpoint=AOAI_ENDPOINT,
            azure_openai_key=AOAI_KEY,
            text_embedding_model=TEXT_EMBEDDING_MODEL
        )
    else:
        print("Doc Index already created. Skipping...")

    # call the create_skillset function with the environment variables
    if IS_SKILLSET_SETUP == "false":
        create_skillset(
            skillset_name=SKILL_SET_NAME,
            index_name=INDEX_NAME,
            ai_search_endpoint=AZURE_SEARCH_ENDPOINT,
            ai_search_key=AZURE_SEARCH_KEY,
            azure_openai_endpoint=AOAI_ENDPOINT,
            azure_openai_key=AOAI_KEY,
            text_embedding_model=TEXT_EMBEDDING_MODEL,
            aiservices_key=AZURE_AISERVICES_KEY
        )
    else:
        print("Skillset already created. Skipping...")

    # call the create_indexer function with the environment variables
    if IS_INDEXER_SETUP == "false":
        create_indexer(
            indexer_name=INDEXER_NAME,
            datasource_name=DATASOURCE_NAME,
            skillset_name=SKILL_SET_NAME,
            index_name=INDEX_NAME,
            ai_search_endpoint=AZURE_SEARCH_ENDPOINT,
            ai_search_key=AZURE_SEARCH_KEY
        )
    else:
        print("Indexer already created. Skipping...")