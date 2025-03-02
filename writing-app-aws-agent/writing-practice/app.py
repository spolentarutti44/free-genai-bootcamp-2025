import streamlit as st
import boto3
import os
from agents.document_processing_agent import DocumentProcessingAgent
from agents.rag_agent import RAGAgent
from config import AWS_REGION, DYNAMODB_TABLE_NAME, TARGET_LANGUAGE

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Initialize agents
document_agent = DocumentProcessingAgent()
rag_agent = RAGAgent()

st.title(f"{TARGET_LANGUAGE} Language Learning Assistant")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Document Writing", "Practice", "History"])

if page == "Document Writing":
    st.header("Document Writing Group")
    
    # Load word groups from database
    word_groups = rag_agent.get_word_groups()
    selected_group = st.selectbox("Select a word group", word_groups)
    
    if selected_group:
        # Get information about the selected word group
        word_group_info = rag_agent.get_word_group_info(selected_group)
        st.write(f"Word group: {word_group_info.get('description', '')}")
        
        # Generate a simple sentence based on the word group
        if st.button("Generate Example Sentence"):
            example_sentence = rag_agent.generate_sentence(selected_group)
            st.success(f"Example: {example_sentence}")
            st.session_state.conversation_history.append({
                "role": "system", 
                "content": f"Generated example sentence for {selected_group}: {example_sentence}"
            })
        
        # User writing area
        st.subheader("Write your sentence")
        user_sentence = st.text_area("Write a sentence in Salish using this word group:")
        
        if st.button("Check Sentence"):
            feedback = rag_agent.check_sentence(user_sentence, selected_group)
            st.session_state.conversation_history.append({
                "role": "user",
                "content": user_sentence
            })
            st.session_state.conversation_history.append({
                "role": "system",
                "content": feedback
            })
            st.info(feedback)
        
        # Document upload
        st.subheader("Or upload your handwritten sentence")
        uploaded_file = st.file_uploader("Upload handwritten sentence", type=["jpg", "jpeg", "png", "pdf"])
        
        if uploaded_file is not None and st.button("Process Document"):
            with st.spinner("Processing document..."):
                extracted_text = document_agent.process_document(uploaded_file)
                st.success("Document processed successfully!")
                st.session_state.conversation_history.append({
                    "role": "user",
                    "content": f"Uploaded document: {uploaded_file.name}"
                })
                st.session_state.conversation_history.append({
                    "role": "system",
                    "content": f"Extracted text: {extracted_text}"
                })
                
                # Display extracted text
                st.subheader("Extracted Text")
                st.write(extracted_text)
                
                # Provide feedback on the extracted text
                feedback = rag_agent.check_sentence(extracted_text, selected_group)
                st.info(feedback)

elif page == "Practice":
    st.header("Practice Area")
    st.write("This area allows you to practice what you've learned.")
    
    practice_type = st.selectbox(
        "What would you like to practice?", 
        ["Vocabulary", "Simple Sentences", "Complex Sentences"]
    )
    
    if practice_type == "Vocabulary":
        word_groups = rag_agent.get_word_groups()
        selected_group = st.selectbox("Select a word group to practice", word_groups)
        
        if selected_group and st.button("Get Practice Words"):
            practice_words = rag_agent.get_practice_words(selected_group)
            st.write("Practice these words:")
            for word in practice_words:
                st.write(f"- {word}")
    
    elif practice_type == "Simple Sentences":
        st.write("Practice constructing simple sentences using the vocabulary you've learned.")
        topic = st.text_input("Enter a topic or theme for your practice:")
        
        if topic and st.button("Generate Practice"):
            practice_sentences = rag_agent.generate_practice_sentences(topic, complexity="simple")
            st.write("Practice translating these sentences:")
            for sentence in practice_sentences:
                st.write(f"- {sentence}")
    
    elif practice_type == "Complex Sentences":
        st.write("Practice constructing more complex sentences with multiple clauses.")
        topic = st.text_input("Enter a topic or theme for your practice:")
        
        if topic and st.button("Generate Practice"):
            practice_sentences = rag_agent.generate_practice_sentences(topic, complexity="complex")
            st.write("Practice translating these sentences:")
            for sentence in practice_sentences:
                st.write(f"- {sentence}")

elif page == "History":
    st.header("Conversation History")
    
    if not st.session_state.conversation_history:
        st.write("No conversation history yet.")
    else:
        for item in st.session_state.conversation_history:
            if item["role"] == "user":
                st.markdown(f"**You:** {item['content']}")
            else:
                st.markdown(f"**Assistant:** {item['content']}")
    
    if st.button("Clear History"):
        st.session_state.conversation_history = []
        st.success("Conversation history cleared.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "This app helps you learn the Salish language through guided practice and document processing."
) 