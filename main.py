# ------------------ FIND ANSWER (FINAL, ROBUST SEARCH LOGIC) ------------------
def find_answer(question, text):
    try:
        # 1. Translate the input question to English for robust keyword extraction
        input_translator = GoogleTranslator(source='auto', target='en')
        search_question = input_translator.translate(text=question)

        # 2. Determine the final answer language
        target_lang_code = 'ar' if st.session_state.language == 'العربية' else 'en'

        # --- CHATBOT SEARCH LOGIC ---
        search_question = search_question.lower()
        
        # Split text into lines/sections
        lines = text.split('\n') 

        # Simplified English keyword extraction
        stop_words = ["what", "is", "the", "are", "of", "a", "an", "how", "when", "where", "me", "about", "tell", "who", "for", "i'm", "i", "do", "you", "and"]
        keywords = [word for word in search_question.split() if word not in stop_words and len(word) > 2]

        # --- Inject Crucial Arabic Search Terms ---
        if 'name' in search_question or 'school' in search_question:
             keywords.append('اسم')
             keywords.append('مدرسة')
        
        # --- FIX: Target header keywords and prepare to grab the next line ---
        is_vision_mission_query = False
        if 'vision' in search_question:
             keywords.append('رؤية')
             is_vision_mission_query = True
        if 'mission' in search_question or 'message' in search_question:
             keywords.append('رسالة')
             is_vision_mission_query = True
        if 'calendar' in search_question or 'date' in search_question or 'hours' in search_question:
            keywords.append('التقويم')
        

        found_text = None
        
        # Loop through lines using index to access the next line
        for i, line in enumerate(lines):
            # 1. Check if the line contains any keyword
            if any(keyword.lower() in line.lower() for keyword in set(keywords)):
                
                # If the query is about Vision or Mission, we return the line AFTER the heading.
                if is_vision_mission_query and i + 1 < len(lines):
                    # Grab the next line, which contains the actual definition
                    found_text = lines[i+1].strip()
                    # Ensure the answer is not empty or just a date/number before accepting
                    if len(found_text) > 5 and not found_text.isdigit(): 
                        break
                    
                # For Name or Calendar, return the line directly (this worked for the Name)
                elif not is_vision_mission_query:
                    found_text = line.strip()
                    break
        
        # If no suitable next line was found, check if the original line itself is the answer
        if not found_text:
            for keyword in set(keywords):
                for line in lines:
                    if keyword.lower() in line.lower():
                        found_text = line.strip()
                        if len(found_text) > 5: # Only accept if it looks like an answer
                            break
                if found_text:
                    break


        # --- Translation and Return ---
        if found_text:
            # Two-Step Translation: Clean the raw text (often Arabic) by translating it to English first
            translation_to_english = GoogleTranslator(source='auto', target='en')
            found_text_en_clean = translation_to_english.translate(text=found_text)

            # Translate the clean English text back to the user's target language
            if target_lang_code != 'en':
                output_translator = GoogleTranslator(source='en', target=target_lang_code)
                final_answer = output_translator.translate(text=found_text_en_clean)
            else:
                final_answer = found_text_en_clean
            
            return final_answer

        return None

    except Exception as e:
        if st.session_state.language == 'العربية':
            return "عذراً، حدث خطأ في الترجمة أو في عملية البحث."
        else:
            return f"Search/Translation Error: Could not process the request. ({str(e)})"
