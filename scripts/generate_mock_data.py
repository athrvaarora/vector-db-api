"""
Generate mock data for the Vector Database with real embeddings from Cohere API.
"""
import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.models.schemas import (
    ChunkMetadata, ChunkCreate,
    DocumentMetadata, DocumentCreate,
    LibraryMetadata, LibraryCreate
)


# Cohere API configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    print("❌ Error: COHERE_API_KEY environment variable not set!")
    print("Please create a .env file with your Cohere API key:")
    print("COHERE_API_KEY=your_api_key_here")
    exit(1)

COHERE_API_URL = "https://api.cohere.ai/v1/embed"


# Sample data for generating diverse content
SAMPLE_TEXTS = [
    # Technology texts
    "Artificial intelligence is revolutionizing how we approach complex problems in computer science.",
    "Machine learning algorithms can identify patterns in large datasets that humans might miss.",
    "Deep learning neural networks have shown remarkable success in image recognition tasks.",
    "Natural language processing enables computers to understand and generate human language.",
    "Cloud computing provides scalable infrastructure for modern web applications.",
    "Blockchain technology offers a decentralized approach to data verification and storage.",
    "Quantum computing promises to solve certain mathematical problems exponentially faster.",
    "Cybersecurity measures are essential for protecting sensitive information in digital systems.",
    
    # Science texts
    "Climate change is one of the most pressing environmental challenges of our time.",
    "Renewable energy sources like solar and wind power are becoming increasingly cost-effective.",
    "Gene editing technologies like CRISPR are opening new possibilities in medicine.",
    "Space exploration continues to reveal fascinating insights about our universe.",
    "Ocean acidification poses a significant threat to marine ecosystems worldwide.",
    "Biodiversity loss is accelerating due to human activities and habitat destruction.",
    "Neuroscience research is helping us understand the complexities of the human brain.",
    "Sustainable agriculture practices are crucial for feeding a growing global population.",
    
    # Business texts
    "Digital transformation is reshaping traditional business models across industries.",
    "Remote work has become a permanent fixture in many organizations post-pandemic.",
    "Data analytics drives strategic decision-making in modern enterprises.",
    "Customer experience has become a key differentiator in competitive markets.",
    "Supply chain resilience is critical for business continuity in uncertain times.",
    "Sustainable business practices are increasingly important to consumers and investors.",
    "Agile methodologies help teams adapt quickly to changing requirements.",
    "Financial technology is democratizing access to banking and investment services.",
    
    # Health & Medicine texts
    "Personalized medicine tailors treatments based on individual genetic profiles.",
    "Telemedicine has expanded access to healthcare services in remote areas.",
    "Mental health awareness has increased significantly in recent years.",
    "Preventive care is more cost-effective than treating diseases after they develop.",
    "Medical imaging technology continues to improve diagnostic accuracy.",
    "Pharmaceutical research is accelerating the development of new treatments.",
    "Wearable devices help individuals monitor their health metrics continuously.",
    "Public health policies play a crucial role in disease prevention and control.",
    
    # Education texts
    "Online learning platforms have democratized access to educational content.",
    "Personalized learning adapts to individual student needs and learning styles.",
    "STEM education prepares students for careers in science and technology.",
    "Critical thinking skills are essential for navigating the modern information landscape.",
    "Educational technology can enhance traditional classroom instruction methods.",
    "Lifelong learning has become necessary in rapidly changing job markets.",
    "Collaborative learning encourages students to work together on complex problems.",
    "Assessment methods are evolving to better measure student understanding and growth.",
    
    # Additional Technology texts
    "Blockchain technology provides transparent and decentralized transaction records.",
    "Internet of Things devices are connecting everyday objects to digital networks.",
    "Edge computing brings data processing closer to the source of data generation.",
    "5G networks enable ultra-fast mobile connectivity and low-latency applications.",
    "Virtual reality creates immersive digital experiences for training and entertainment.",
    "Augmented reality overlays digital information onto the physical world.",
    "Robotics automation is transforming manufacturing and service industries.",
    "DevOps practices streamline software development and deployment processes.",
    
    # Additional Science texts
    "CRISPR gene editing technology enables precise modifications to DNA sequences.",
    "Quantum entanglement demonstrates mysterious connections between particles.",
    "Dark matter comprises most of the universe but remains largely undetectable.",
    "Synthetic biology engineers biological systems for useful applications.",
    "Nanotechnology manipulates matter at the molecular and atomic scale.",
    "Fusion energy research aims to replicate the sun's power generation process.",
    "Microbiome research reveals the importance of bacterial communities in health.",
    "Stem cell therapy offers potential treatments for degenerative diseases.",
    
    # Additional Business texts
    "Artificial intelligence is automating routine business processes and decisions.",
    "E-commerce platforms have revolutionized retail and consumer behavior.",
    "Social media marketing leverages user-generated content and influencer partnerships.",
    "Cloud computing provides scalable and cost-effective IT infrastructure solutions.",
    "Cryptocurrency and digital assets are emerging as alternative investment vehicles.",
    "Supply chain transparency helps companies track products from source to consumer.",
    "Customer relationship management systems centralize client interaction data.",
    "Business intelligence tools transform raw data into actionable insights."
]

LIBRARY_NAMES = [
    "AI Research Collection", "Climate Science Database", "Business Strategy Library",
    "Medical Research Archive", "Technology Innovation Hub", "Educational Resources",
    "Scientific Papers Collection", "Industry Reports Database", "Financial Analysis Hub",
    "Cybersecurity Knowledge Base", "Data Science Repository", "Machine Learning Papers"
]

DOCUMENT_TITLES = [
    "Introduction to Machine Learning", "Climate Change Impacts", "Digital Business Transformation",
    "Advances in Gene Therapy", "Quantum Computing Fundamentals", "Remote Work Best Practices",
    "Renewable Energy Technologies", "Cybersecurity Framework", "Data Analytics Strategy",
    "Sustainable Development Goals", "Artificial Neural Networks", "Healthcare Innovation",
    "Educational Technology Trends", "Financial Technology Evolution", "Deep Learning Architectures",
    "Blockchain Applications", "Cloud Computing Security", "IoT Implementation Guide",
    "Autonomous Vehicle Technology", "Biotechnology Innovations", "Space Exploration Updates",
    "Cryptocurrency Analysis", "Supply Chain Optimization", "Customer Experience Design",
    "Agile Project Management", "DevOps Best Practices", "API Design Principles",
    "Database Performance Tuning", "Mobile App Development", "User Interface Guidelines"
]

AUTHORS = [
    "Dr. Sarah Johnson", "Prof. Michael Chen", "Dr. Emily Rodriguez", "Prof. David Kim",
    "Dr. Lisa Anderson", "Prof. Robert Taylor", "Dr. Maria Garcia", "Prof. James Wilson",
    "Dr. Jennifer Lee", "Prof. Thomas Brown", "Dr. Anna Petrov", "Prof. Alex Thompson",
    "Dr. Rachel Green", "Prof. Kevin Zhang", "Dr. Amanda White", "Prof. Marcus Johnson",
    "Dr. Samantha Davis", "Prof. Daniel Miller", "Dr. Rebecca Turner", "Prof. Steven Clark"
]

TAGS = [
    "machine-learning", "climate-science", "business-strategy", "healthcare", "technology",
    "education", "research", "innovation", "sustainability", "digital-transformation",
    "artificial-intelligence", "data-science", "cybersecurity", "renewable-energy",
    "blockchain", "quantum-computing", "biotechnology", "fintech", "devops", "cloud-computing",
    "mobile-development", "web-development", "database", "api-design", "user-experience",
    "agile", "automation", "analytics", "visualization"
]


async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings from Cohere API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                COHERE_API_URL,
                headers={
                    "Authorization": f"Bearer {COHERE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "texts": texts,
                    "model": "embed-english-v3.0",
                    "input_type": "search_document"
                },
                timeout=30.0
            )
            response.raise_for_status()
            
            data = response.json()
            return data["embeddings"]
            
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            # Fallback to random embeddings for testing
            return [[random.random() for _ in range(1024)] for _ in texts]


def generate_random_date(start_date: datetime, end_date: datetime) -> datetime:
    """Generate a random date between start_date and end_date."""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)


async def generate_mock_data() -> dict:
    """Generate comprehensive mock data for the vector database."""
    print("Generating mock data with real embeddings...")
    
    # Generate embeddings for all sample texts
    print("Getting embeddings from Cohere API...")
    embeddings = await get_embeddings(SAMPLE_TEXTS)
    print(f"Generated {len(embeddings)} embeddings")
    
    mock_data = {
        "libraries": [],
        "documents": [],
        "chunks": []
    }
    
    # Generate libraries (increased to 8)
    for i in range(8):
        library_id = uuid4()
        
        library_data = LibraryCreate(
            metadata=LibraryMetadata(
                name=LIBRARY_NAMES[i],
                description=f"A comprehensive collection focused on {LIBRARY_NAMES[i].lower()}",
                owner=random.choice(AUTHORS),
                tags=random.sample(TAGS, random.randint(2, 4)),
                is_public=random.choice([True, False])
            )
        )
        
        library_dict = {
            "id": str(library_id),
            "create_data": json.loads(library_data.model_dump_json()),
            "documents": []
        }
        
        # Generate documents for this library (increased range)
        num_documents = random.randint(3, 6)
        for j in range(num_documents):
            document_id = uuid4()
            
            document_data = DocumentCreate(
                metadata=DocumentMetadata(
                    title=random.choice(DOCUMENT_TITLES),
                    description=f"Detailed analysis and research on {random.choice(DOCUMENT_TITLES).lower()}",
                    author=random.choice(AUTHORS),
                    tags=random.sample(TAGS, random.randint(1, 3)),
                    category=random.choice(["research", "analysis", "report", "tutorial"]),
                    file_type=random.choice(["pdf", "docx", "txt", "html"])
                ),
                library_id=library_id
            )
            
            document_dict = {
                "id": str(document_id),
                "create_data": json.loads(document_data.model_dump_json()),
                "chunks": []
            }
            
            # Generate chunks for this document (increased range)
            num_chunks = random.randint(4, 8)
            chunk_indices = random.sample(range(len(SAMPLE_TEXTS)), num_chunks)
            
            for k, text_idx in enumerate(chunk_indices):
                chunk_id = uuid4()
                
                chunk_data = ChunkCreate(
                    text=SAMPLE_TEXTS[text_idx],
                    embedding=embeddings[text_idx],
                    metadata=ChunkMetadata(
                        source=f"page_{k+1}",
                        author=random.choice(AUTHORS),
                        tags=random.sample(TAGS, random.randint(1, 2)),
                        language="en",
                        char_count=len(SAMPLE_TEXTS[text_idx])
                    ),
                    document_id=document_id
                )
                
                chunk_dict = {
                    "id": str(chunk_id),
                    "create_data": json.loads(chunk_data.model_dump_json())
                }
                
                document_dict["chunks"].append(chunk_dict)
                mock_data["chunks"].append(chunk_dict)
            
            library_dict["documents"].append(document_dict)
            mock_data["documents"].append(document_dict)
        
        mock_data["libraries"].append(library_dict)
    
    return mock_data


async def populate_database(base_url: str = "http://localhost:8000/api/v1") -> None:
    """Populate the database with mock data via API calls."""
    print(f"Populating database at {base_url}...")
    
    mock_data = await generate_mock_data()
    
    async with httpx.AsyncClient() as client:
        try:
            # Create libraries
            for library in mock_data["libraries"]:
                print(f"Creating library: {library['create_data']['metadata']['name']}")
                
                response = await client.post(
                    f"{base_url}/libraries",
                    json=library["create_data"],
                    timeout=30.0
                )
                response.raise_for_status()
                created_library = response.json()
                actual_library_id = created_library["id"]
                
                # Create documents
                for document in library["documents"]:
                    document["create_data"]["library_id"] = actual_library_id
                    
                    print(f"  Creating document: {document['create_data']['metadata']['title']}")
                    
                    response = await client.post(
                        f"{base_url}/documents",
                        json=document["create_data"],
                        timeout=30.0
                    )
                    response.raise_for_status()
                    created_document = response.json()
                    actual_document_id = created_document["id"]
                    
                    # Create chunks
                    for chunk in document["chunks"]:
                        chunk["create_data"]["document_id"] = actual_document_id
                        
                        response = await client.post(
                            f"{base_url}/chunks",
                            json=chunk["create_data"],
                            timeout=30.0
                        )
                        response.raise_for_status()
                
                # Index the library
                print(f"  Indexing library with flat algorithm...")
                response = await client.post(
                    f"{base_url}/libraries/{actual_library_id}/index?index_type=flat",
                    timeout=30.0
                )
                response.raise_for_status()
            
            print("Mock data population completed successfully!")
            
        except Exception as e:
            print(f"Error populating database: {e}")
            raise


def save_mock_data_to_file(mock_data: dict, filename: str = "mock_data.json") -> None:
    """Save mock data to a JSON file for inspection."""
    # Convert UUIDs to strings for JSON serialization
    def json_serializer(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    with open(filename, 'w') as f:
        json.dump(mock_data, f, indent=2, default=json_serializer)
    
    print(f"Mock data saved to {filename}")


async def main():
    """Main function to generate and optionally populate mock data."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate mock data for Vector Database")
    parser.add_argument("--populate", action="store_true", 
                       help="Populate the database via API calls")
    parser.add_argument("--save", action="store_true", 
                       help="Save mock data to JSON file")
    parser.add_argument("--url", default="http://localhost:8000/api/v1",
                       help="Base URL for API calls")
    
    args = parser.parse_args()
    
    if args.populate:
        await populate_database(args.url)
    else:
        mock_data = await generate_mock_data()
        
        if args.save:
            save_mock_data_to_file(mock_data)
        
        print(f"Generated comprehensive mock data:")
        print(f"  Libraries: {len(mock_data['libraries'])}")
        print(f"  Documents: {len(mock_data['documents'])}")
        print(f"  Chunks: {len(mock_data['chunks'])}")
        print(f"  Sample texts: {len(SAMPLE_TEXTS)}")
        print(f"  Authors: {len(AUTHORS)}")
        print(f"  Tags: {len(TAGS)}")


if __name__ == "__main__":
    asyncio.run(main())