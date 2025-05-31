from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.agent import ResearchAgent
from app.utils.logger import logger

router = APIRouter(tags=["Query"])
agent = ResearchAgent()

@router.post("/ask", response_model=QueryResponse)
async def ask_agent(request: QueryRequest):
    try:
        logger.info(f"Received query: {request.query}")
        result = await agent.handle(request.query)
        return result
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 
    
@router.post("/ask-test", response_model=QueryResponse)
async def ask_agent_test(request: QueryRequest):
    try:
        logger.info(f"Received test query: {request.query}")
        # Hardcoded response matching the specified output
        result = QueryResponse(
            thought_process={
                "sub_questions": [
                    "What are the fundamental principles and concepts of quantum computing?",
                    "How does quantum computing differ from classical computing?",
                    "What are some potential applications and implications of quantum computing?"
                ],
                "search_results": {
                    "What are the fundamental principles and concepts of quantum computing?": [
                        {
                            "title": "Quantum computing fundamentals | IBM Quantum Learning",
                            "link": "https://learning.quantum.ibm.com/course/quantum-business-foundations/quantum-computing-fundamentals",
                            "snippet": "He guides you to visualize the three core principles of quantum computing: superposition, entanglement, and interference. With these properties, quantum ...",
                            "displayLink": "learning.quantum.ibm.com"
                        },
                        {
                            "title": "What is Quantum Computing? - Quantum Computing Explained - AWS",
                            "link": "https://aws.amazon.com/what-is/quantum-computing/",
                            "snippet": "Quantum principles require a new dictionary of terms to be fully understood, terms that include superposition, entanglement, and decoherence. Let's understand ...",
                            "displayLink": "aws.amazon.com"
                        },
                        {
                            "title": "Quantum Computing Basics: A Beginner's Guide",
                            "link": "https://www.bluequbit.io/quantum-computing-basics",
                            "snippet": "Quantum theory is a set of principles that govern the behavior of matter and energy on a subatomic level. Unlike classical physics, which describes the behavior ...",
                            "displayLink": "www.bluequbit.io"
                        }
                    ],
                    "How does quantum computing differ from classical computing?": [
                        {
                            "title": "Quantum vs Classical Computing | Quantum Threat | Quantropi",
                            "link": "https://www.quantropi.com/quantum-versus-classical-computing-and-the-quantum-threat/",
                            "snippet": "A quantum computer uses a quantum property called superposition or qubits to store data. Unlike a classical computer whose bits of data can exist as either a ...",
                            "displayLink": "www.quantropi.com"
                        },
                        {
                            "title": "I've heard that quantum computers won't replace classical ...",
                            "link": "https://www.reddit.com/r/QuantumComputing/comments/om56op/ive_heard_that_quantum_computers_wont_replace/",
                            "snippet": "Jul 17, 2021 ... Quantum computing is useful for problems where the answers are true AND false simultaneously, classical computing handles true OR false problems ...",
                            "displayLink": "www.reddit.com"
                        },
                        {
                            "title": "Classical vs. quantum computing: What are the differences ...",
                            "link": "https://www.techtarget.com/searchdatacenter/tip/Classical-vs-quantum-computing-What-are-the-differences",
                            "snippet": "Apr 23, 2025 ... First, while classical computers use bits -- the familiar 0s and 1s -- of binary computing to represent data and logic, quantum computers use ...",
                            "displayLink": "www.techtarget.com"
                        }
                    ]
                },
                "analysis_steps": [
                    "1. Initial Query Analysis: Breaking down 'Explain quantum computing basics.' into focused sub-questions",
                    "2. Generated 3 sub-questions to explore different aspects of the topic",
                    "3.1 Researching sub-question 1: 'What are the fundamental principles and concepts of quantum computing?'",
                    "   - Found 3 relevant sources",
                    "   - Key sources include: Quantum computing fundamentals..., What is Quantum Computing? - Q...",
                    "3.2 Researching sub-question 2: 'How does quantum computing differ from classical computing?'",
                    "   - Found 3 relevant sources",
                    "   - Key sources include: Quantum vs Classical Computing..., I've heard that quantum comput...",
                    "3.3 Researching sub-question 3: 'What are some potential applications and implications of quantum computing?'",
                    "   - Found 0 relevant sources",
                    "4. Content Analysis:",
                    "   - Extracting and analyzing information from each source",
                    "   - Identifying key insights and patterns",
                    "   - Cross-referencing information across sources",
                    "5. Synthesis:",
                    "   - Combining findings from all sub-questions",
                    "   - Identifying common themes and unique perspectives",
                    "   - Preparing comprehensive response"
                ],
                "content_summary": {
                    "What are the fundamental principles and concepts of quantum computing?": "This content provides a basic understanding of the principles and concepts of quantum computing. It explains the difference between quantum computing and classical computing, and between qubits and bits. The content uses a metaphor of the transition from black-and-white to color photography to illustrate the revolutionary paradigm shift brought about by quantum computing, akin to the new possibilities opened up by the advent of color film in photography.",
                    "How does quantum computing differ from classical computing?": "The content outlines the fundamental differences between quantum and classical computing. Quantum computing uses quantum properties or qubits that can exist as both 0 and 1 simultaneously, enabling them to perform multiple calculations at once, which gives quantum computers a speed advantage and problem-solving capability far beyond classical ones. Furthermore, the content mentions the prospective applications of quantum computing in fields like security and communications, and the difference in how algorithms are executed on quantum versus classical computers."
                }
            },
            answer="""
# Quantum Computing Basics

Quantum computing is an emerging field of computer science that leverages the principles of quantum physics to perform complex calculations more quickly and efficiently than traditional, or 'classical', computers. This report will provide an overview of the fundamental principles of quantum computing, compare and contrast classical and quantum computing, and discuss the potential applications and challenges of this technology.

## Fundamental Principles of Quantum Computing

Quantum computing is based on the principles of quantum mechanics, which describe the behavior of particles at the subatomic level ([3]). Unlike classical physics, which describes the behavior of macroscopic objects, quantum physics involves phenomena that can seem counterintuitive, such as superposition, entanglement, and the uncertainty principle.

### Qubits

At the heart of quantum computing is the qubit, or quantum bit. Unlike classical bits, which can either be 0 or 1, qubits can exist in a superposition of states, meaning they can be both 0 and 1 simultaneously ([1]). This ability allows quantum computers to perform many calculations in parallel, significantly increasing their computational power.

### Quantum Gates and Circuits

Quantum gates and circuits are the building blocks of quantum computing. Quantum gates are operations that transform the state of qubits, and quantum circuits are sequences of these gate operations that perform a specific computation ([1]). These quantum operations are analogous to the logic gates used in classical computing but are capable of more complex transformations due to the quantum nature of the qubits.

### Quantum Phenomena: Superposition, Entanglement, and Interference

Superposition, entanglement, and interference are quantum phenomena that are fundamental to quantum computing ([1], [3]).

* Superposition allows qubits to exist in multiple states simultaneously, enabling quantum computers to perform many calculations at once.
* Entanglement is a quantum effect where two qubits become linked, such that the state of one instantaneously affects the state of the other, regardless of the distance between them.
* Interference is a phenomenon where quantum states can interact and interfere with each other, which is used in quantum computing to manipulate the probabilities of qubit states.

## Quantum vs. Classical Computing

While classical computers use bits to process information in a binary format (0s and 1s), quantum computers use qubits that can exist in a superposition of states ([1], [4], [6]). This fundamental difference allows quantum computers to process a vast number of possibilities simultaneously, solving certain problems much faster than classical computers.

Quantum computing also introduces the concept of quantum gates and quantum circuits, which are distinct from classical gates and circuits ([1], [4]). Quantum gates manipulate the state of qubits, and quantum circuits are made up of a sequence of these gate operations.

Another important distinction is that quantum computers have a probabilistic nature, meaning that they give a probability of an outcome rather than a definite answer ([6]). This contrasts with classical computers, which always return the same result for a given input.

## Applications and Challenges

Quantum computers have the potential to revolutionize various fields, including AI, cybersecurity, optimization, and modeling ([6]). They could, for example, significantly enhance encryption algorithms, making communications more secure ([4]).

However, several challenges need to be addressed before quantum computers can be widely used. These include developing fault-tolerant quantum computers, scaling up the number of qubits, and maintaining qubit coherence ([1], [2]).

## Conclusion

Quantum computing, while still in its infancy, holds great promise for solving complex problems that are currently beyond the reach of classical computers. By harnessing the principles of quantum physics, quantum computers can process information in fundamentally new ways. However, several technical challenges need to be overcome before this technology can be fully realized. Despite these challenges, the potential impact of quantum computing on various industries is substantial, making it a critical area of research and development.
            """,
            sources=[
                {
                    "title": "Quantum computing fundamentals | IBM Quantum Learning",
                    "url": "https://learning.quantum.ibm.com/course/quantum-business-foundations/quantum-computing-fundamentals"
                },
                {
                    "title": "What is Quantum Computing? - Quantum Computing Explained - AWS",
                    "url": "https://aws.amazon.com/what-is/quantum-computing/"
                },
                {
                    "title": "Quantum Computing Basics: A Beginner's Guide",
                    "url": "https://www.bluequbit.io/quantum-computing-basics"
                },
                {
                    "title": "Quantum vs Classical Computing | Quantum Threat | Quantropi",
                    "url": "https://www.quantropi.com/quantum-versus-classical-computing-and-the-quantum-threat/"
                },
                {
                    "title": "I've heard that quantum computers won't replace classical ...",
                    "url": "https://www.reddit.com/r/QuantumComputing/comments/om56op/ive_heard_that_quantum_computers_wont_replace/"
                },
                {
                    "title": "Classical vs. quantum computing: What are the differences ...",
                    "url": "https://www.techtarget.com/searchdatacenter/tip/Classical-vs-quantum-computing-What-are-the-differences"
                }
            ]
        )
        return result
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing test query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")