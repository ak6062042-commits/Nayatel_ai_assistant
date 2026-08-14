# Data Directory and Raw Dataset

## Overview

The `data` directory contains the documents used by the Nayatel AI Assistant's RAG pipeline.

It is divided into two main sections:

```text
data/
├── raw/
└── processed/
    ├── cleaned/
    ├── chunks/
    └── vector_db/
```

The `raw` directory contains the original documents collected from the Nayatel website.

The `processed` directory contains the different outputs generated as the documents move through the RAG data pipeline.

---

# Data Directory Structure

```text
data/
│
├── raw/
│   └── Original Nayatel PDF documents
│
└── processed/
    │
    ├── cleaned/
    │   └── Cleaned document text
    │
    ├── chunks/
    │   └── Chunked document data
    │
    └── vector_db/
        └── ChromaDB vector database
```

The directories represent different stages of the document processing pipeline.

```text
Raw PDFs
   ↓
Cleaning
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Database
   ↓
Retriever
   ↓
LLM
```

---

# `data/raw`

The `raw` directory contains the original PDF files collected from the Nayatel website.

The data was collected on:

```text
9 July 2026
```

All of the raw data used by the project is included with the repository.

The raw documents are kept separately from the processed data so that the original source material remains available if the processing pipeline needs to be run again.

---

# Raw Dataset Statistics

The current dataset contains:

* **44 total PDF files**
* **14 unique categories**

The categories are:

```text
blog
Contact
discounts
faq
Hardware_Changes
manuals
Payment
prices
Security_Advisory
gaming
home security
internet
telephone
video
```

These categories are represented through the organization of the raw documents and are also used as metadata during the processing pipeline.

---

# Raw Dataset Categories

| Category            | Purpose                                              |
| ------------------- | ---------------------------------------------------- |
| `blog`              | General Nayatel articles and informational content.  |
| `Contact`           | Contact and support-related information.             |
| `discounts`         | Discount and promotional information.                |
| `faq`               | Frequently asked questions.                          |
| `Hardware_Changes`  | Information related to hardware changes and updates. |
| `manuals`           | User manuals and device documentation.               |
| `Payment`           | Payment methods and payment-related information.     |
| `prices`            | Package and pricing information.                     |
| `Security_Advisory` | Security advisories and related information.         |
| `gaming`            | Gaming-related services and information.             |
| `home security`     | Home security products and services.                 |
| `internet`          | Internet-related services and information.           |
| `telephone`         | Telephone services and information.                  |
| `video`             | TV, video, and related services.                     |

---

# Raw PDF Files

The following 44 PDF files are included in the raw dataset.

## Blog

The `blog` category contains general informational articles collected from the Nayatel website.

```text
5G in Pakistan.pdf
Benefits of fiber internet for homes and businesses.pdf
Best Internet Speed for Freelancers in Pakistan.pdf
Difference between 2.4 GHz and 5 GHz.pdf
Fiber vs DSL vs 4G_5G.pdf
How Many Devices Can Your Internet Plan Actually Support.pdf
How to Optimize Your Fiber Internet at Home.pdf
How to set up your fiber optic router.pdf
IPTV vs Cable TV.pdf
Nayatel Is Now Serving Enterprises Around the World.pdf
ONT Lights .pdf
What Is Fiber optic.pdf
Why Fiber Internet is Better for Gaming and Streaming.pdf
```

These documents provide general technical and service-related information that can be useful when answering customer questions.

---

## Contact

```text
Contact us.pdf
```

Contains contact and support-related information.

---

## Discounts

```text
discounts.pdf
```

Contains information related to available discounts and promotional offers.

---

## FAQ

```text
faq.pdf
```

Contains frequently asked questions and their corresponding information.

---

## Hardware Changes

```text
Hardware Changes.pdf
```

Contains information related to hardware changes.

---

## Manuals

The `manuals` category contains device manuals and hardware-related documentation.

```text
edge ont.pdf
hdmi cec settings.pdf
hik vision.pdf
Huawei GPON dual band ont user manaul.pdf
huawei gpon.pdf
huawei windows application for nwatch.pdf
naya box user manual.pdf
Ruijie.pdf
tplink router.pdf
ups manual.pdf
VOC.pdf
Wireless Air Remote Mouse.pdf
```

These documents are particularly useful for technical support questions involving device setup, configuration, and troubleshooting.

---

## Payment

```text
Payment options.pdf
```

Contains information about available payment options.

---

## Prices

```text
Nayatel_Pricing_By_Location.pdf
```

Contains Nayatel pricing information organized by location.

This document is especially important for questions involving package prices and location-dependent pricing.

---

## Security Advisory

```text
Security Advisories.pdf
```

Contains security-related advisory information.

---

## Gaming

```text
exitlag.pdf
```

Contains information related to the ExitLag gaming service.

---

## Home Security

```text
Optimus.pdf
eview.pdf
n_watch.pdf
safe_web.pdf
```

Contains information about Nayatel's home security and related services.

---

## Internet

```text
speed_up.pdf
Unlimited_bundle.pdf
```

Contains internet-related services and package information.

---

## Telephone

```text
telephone.pdf
```

Contains information related to Nayatel telephone services.

---

## Video

```text
cabel_tv.pdf
digital_box.pdf
naya_box.pdf
naya_tv.pdf
```

Contains information related to Nayatel's video and TV services.

---

# `data/processed`

The `processed` directory contains the outputs generated after processing the raw documents.

It is divided into three stages:

```text
processed/
├── cleaned/
├── chunks/
└── vector_db/
```

Each directory represents a different stage of the RAG ingestion pipeline.

---

# `processed/cleaned`

The `cleaned` directory stores the cleaned version of the extracted document text.

The processing flow is approximately:

```text
Raw PDF
   ↓
PDF Text Extraction
   ↓
Text Cleaning
   ↓
Cleaned Data
```

Cleaning removes unnecessary formatting and text noise from the extracted PDF content.

Examples of processing may include:

* Removing excessive whitespace
* Normalizing line breaks
* Cleaning unwanted characters
* Preparing the extracted text for chunking

The cleaned data becomes the input for the next stage of the pipeline.

---

# `processed/chunks`

The `chunks` directory contains the documents after they have been divided into smaller text chunks.

The processing flow is:

```text
Cleaned Text
    ↓
Chunking
    ↓
Smaller Text Sections
```

Chunking is necessary because sending an entire PDF to the embedding model or LLM is generally not practical.

Instead, documents are divided into smaller sections that can be independently embedded and retrieved.

Each chunk can also contain metadata such as:

```text
source
page
category
chunk_index
```

This metadata is later used by the retriever.

For example:

```text
Document
    ↓
Chunk 0
Chunk 1
Chunk 2
Chunk 3
...
```

The `chunk_index` allows the retriever to identify neighboring chunks and expand the retrieved context when required.

---

# `processed/vector_db`

The `vector_db` directory contains the persistent ChromaDB vector database.

The processing flow is:

```text
Text Chunks
    ↓
Embedding Model
    ↓
Vector Embeddings
    ↓
ChromaDB
```

Each chunk is converted into an embedding vector and stored in ChromaDB along with its associated metadata and text.

The retriever later connects to this database to perform similarity searches.

This is the main knowledge storage used by the RAG system.

---

# Relationship Between the Directories

The three processed directories are connected sequentially:

```text
                    data/
                     │
                     ▼
                    raw/
                 Original PDFs
                     │
                     ▼
                  cleaned/
              Cleaned Text Data
                     │
                     ▼
                  chunks/
              Chunked Documents
                     │
                     ▼
                 vector_db/
              ChromaDB Embeddings
                     │
                     ▼
                  Retriever
                     │
                     ▼
                 Relevant Context
                     │
                     ▼
                    LLM
```

Each stage depends on the output of the previous stage.

---

# Why the Raw Data Is Kept

The original PDFs are intentionally kept unchanged.

This provides a source of truth for the project and allows the processing pipeline to be regenerated if needed.

For example:

```text
Raw PDFs
   ↓
New cleaning logic
   ↓
New chunks
   ↓
New embeddings
   ↓
Updated vector database
```

Without the raw documents, changes to the processing pipeline would require recollecting the original data.

---

# Dataset Role in the RAG System

The data directory forms the knowledge base of the chatbot.

The chatbot does not directly send all 44 PDFs to the LLM.

Instead, the documents are progressively processed:

```text
44 Raw PDFs
      ↓
Extract Text
      ↓
Clean Text
      ↓
Create Chunks
      ↓
Generate Embeddings
      ↓
Store in ChromaDB
      ↓
User asks a question
      ↓
Retriever searches ChromaDB
      ↓
Relevant chunks are returned
      ↓
Context is added to the prompt
      ↓
LLM generates the response
```

This approach allows the chatbot to search a relatively large collection of documents without needing to load the entire dataset into every LLM request.

---

# Dataset Snapshot

| Item                       | Value                       |
| -------------------------- | --------------------------- |
| Source                     | Nayatel website             |
| Collection date            | 9 July 2026                 |
| Total PDF files            | 44                          |
| Unique categories          | 14                          |
| Raw data location          | `data/raw/`                 |
| Cleaned data               | `data/processed/cleaned/`   |
| Chunked data               | `data/processed/chunks/`    |
| Vector database            | `data/processed/vector_db/` |
| Vector database technology | ChromaDB                    |

---

# Notes

The dataset represents the information available during the collection date of **9 July 2026**. Since website content, packages, prices, policies, and services can change over time, the chatbot's answers are limited to the information available in this collected dataset.

The raw PDFs are included with the repository so that the complete ingestion pipeline can be reproduced from the original source documents.
