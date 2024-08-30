# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


import os

import docx
import gradio as gr
from hugegraph_llm.config import resource_path, settings
from hugegraph_llm.indices.vector_index import VectorIndex
from hugegraph_llm.models.embeddings.init_embedding import Embeddings
from hugegraph_llm.models.llms.init_llm import LLMs
from hugegraph_llm.operators.kg_construction_task import KgBuilder
from hugegraph_llm.utils.hugegraph_utils import get_hg_client


def get_vector_index_info():
    vector_index = VectorIndex.from_index_file(str(os.path.join(resource_path, settings.graph_name, "chunks")))
    return {
        "embed_dim": vector_index.index.d,
        "num_vectors": vector_index.index.ntotal,
        "num_properties": len(vector_index.properties)
    }


def clean_vector_index():
    VectorIndex.clean(str(os.path.join(resource_path, settings.graph_name, "chunks")))


def build_vector_index(input_file, input_text):
    if input_file:
        texts = []
        for file in input_file:
            full_path = file.name
            if full_path.endswith(".txt"):
                with open(full_path, "r", encoding="utf-8") as f:
                    texts.append(f.read())
            elif full_path.endswith(".docx"):
                text = ""
                doc = docx.Document(full_path)
                for para in doc.paragraphs:
                    text += para.text
                    text += "\n"
                texts.append(text)
            elif full_path.endswith(".pdf"):
                # TODO: support PDF file
                raise gr.Error("PDF will be supported later! Try to upload text/docx now")
            else:
                raise gr.Error("Please input txt or docx file.")
    elif input_text:
        texts = [input_text]
    else:
        raise gr.Error("Please input text or upload file.")
    builder = KgBuilder(LLMs().get_llm(), Embeddings().get_embedding(), get_hg_client())
    return builder.chunk_split(texts, "paragraph", "zh").build_vector_index().run()
