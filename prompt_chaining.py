# -*- coding: utf-8 -*-

# ***************************************************
# * File        : prompt_chaining.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-09-17
# * Version     : 1.0.091723
# * Description : description
# * Link        : link
# * Requirement : 相关模块版本需求(例如: numpy >= 2.1.0)
# ***************************************************

__all__ = []

# python libraries
import os
import sys
from pathlib import Path
ROOT = str(Path.cwd())
if ROOT not in sys.path:
    sys.path.append(ROOT)
from dotenv import find_dotenv, load_dotenv
import warnings
warnings.filterwarnings("ignore")

# from langchain_core import ChatOpenAI
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ['LOG_NAME'] = LOGGING_LABEL
from utils.log_util import logger


# load env variables
from dotenv import find_dotenv, load_dotenv
_ = load_dotenv(find_dotenv(), override=True)
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
logger.info(f'OPENAI_API_KEY: {OPENAI_API_KEY}')


# ------------------------------
# Initialize the Language Model (using ChatOpenAI is recommended)
# ------------------------------
# llm = ChatOpenAI(temperature=0)
llm = init_chat_model("openai:gpt-4.1", temperature=0)

# ------------------------------
# prompt
# ------------------------------
# Prompt 1: Extract Information
prompt_extract = ChatPromptTemplate.from_template(
    "Extract the technical specifications from the following text:\n\n{text_input}"
)

# Prompt 2: Transform to JSON
prompt_transform = ChatPromptTemplate.from_template(
    "Transform the following specifications into a JSON object with 'cpu', 'memory', and 'storage' as keys:\n\n{specifications}"
)

# ------------------------------
# Build the Chain using LCEL
# ------------------------------
# The StrOutputParser() converts the LLM's message output to a simple string.
extraction_chain = prompt_extract | llm | StrOutputParser()

# The full chain passes the output of the extraction chain into the 'specifications'
# variable for the transformation prompt.
full_chain = (
    {"specifications": extraction_chain}
    | prompt_transform
    | llm
    | StrOutputParser()
)

# ------------------------------
# Run the Chain
# ------------------------------
input_text = "The new laptop model features a 3.5 GHz octa-core processor, 16GB of RAM, and a 1TB NVMe SSD."

# Execute the chain with the input text dictionary.
final_result = full_chain.invoke({"text_input": input_text})

print("\n--- Final JSON Output")
print(final_result)




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
