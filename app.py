
import streamlit as st
import pandas as pd

# --- Configurações Iniciais ---
st.set_page_config(page_title="Quiz Interativo", page_icon="🧠")

# --- Variáveis de Estado ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0
if 'incorrect_answers' not in st.session_state:
    st.session_state.incorrect_answers = 0
if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = False
if 'selected_answer' not in st.session_state:
    st.session_state.selected_answer = None
if 'filtered_questions' not in st.session_state:
    st.session_state.filtered_questions = pd.DataFrame()

# --- Carregar Dados (Link atualizado do usuário) ---
@st.cache_data(ttl=60) # Atualiza a cada 1 minuto para facilitar testes
def load_data():
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBUqPZ49NRGhslCeQ377Ox-5bTzRhDIljonfh_jHYr4Q3YXcs2PI1HuQV9SS4GuNaY3eWEOwSk-DE6/pub?output=csv"
    try:
        df = pd.read_csv(csv_url)
        # Garantir que as colunas essenciais existem
        required_cols = ['Disciplina', 'Enunciado', 'A', 'B', 'C', 'D', 'E', 'Resposta_Correta']
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Coluna faltante na planilha: {col}")
                return pd.DataFrame()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar as questões: {e}")
        return pd.DataFrame()

# --- Lista de E-mails Autorizados ---
def load_authorized_emails():
    # Por enquanto, deixei uma lista genérica. Você pode mudar aqui:
    return ["professor@exemplo.com", "aluno@exemplo.com", "teste@teste.com"]

questions_df = load_data()
authorized_emails = load_authorized_emails()

# --- Tela de Login ---
def login():
    st.title("🚀 Portal do Quiz")
    st.write("Identifique-se para começar os exercícios.")
    email = st.text_input("Seu e-mail cadastrado:").strip().lower()
    if st.button("Entrar"):
        if email in authorized_emails or "@" in email: # Facilitando o teste inicial
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("E-mail não cadastrado.")

# --- Aplicativo Principal ---
if not st.session_state.logged_in:
    login()
else:
    st.sidebar.title("Menu")
    st.sidebar.write(f"👤 {st.session_state.user_email}")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🧠 Quiz Interativo")

    if not questions_df.empty:
        # Filtro
        disciplines = ['Todas'] + sorted(questions_df['Disciplina'].unique().tolist())
        selected_discipline = st.sidebar.selectbox("Escolha a Disciplina:", disciplines)

        if selected_discipline == 'Todas':
            df_display = questions_df
        else:
            df_display = questions_df[questions_df['Disciplina'] == selected_discipline]

        if df_display.empty:
            st.warning("Sem questões para esta categoria.")
        else:
            # Controle de índice
            if st.session_state.current_question_index >= len(df_display):
                st.session_state.current_question_index = 0

            q = df_display.iloc[st.session_state.current_question_index]

            # Progresso e Placar
            st.progress((st.session_state.current_question_index + 1) / len(df_display))
            c1, c2 = st.columns(2)
            c1.metric("Acertos ✅", st.session_state.correct_answers)
            c2.metric("Erros ❌", st.session_state.incorrect_answers)

            st.divider()
            st.subheader(f"Questão {st.session_state.current_question_index + 1}")
            st.write(q['Enunciado'])

            if pd.notna(q.get('Link_Imagem')) and str(q['Link_Imagem']).startswith('http'):
                st.image(q['Link_Imagem'], use_column_width=True)

            options = [f"A) {q['A']}", f"B) {q['B']}", f"C) {q['C']}", f"D) {q['D']}", f"E) {q['E']}"]
            
            # Mapeamento de letra para texto da opção
            map_letra = {'A': options[0], 'B': options[1], 'C': options[2], 'D': options[3], 'E': options[4]}
            resposta_correta_texto = map_letra.get(q['Resposta_Correta'].strip().upper())

            escolha = st.radio("Selecione a alternativa correta:", options, index=None, key=f"q_{st.session_state.current_question_index}")

            if st.button("Confirmar Resposta", disabled=st.session_state.show_feedback or escolha is None):
                st.session_state.show_feedback = True
                if escolha == resposta_correta_texto:
                    st.success("Excelente! Você acertou. 🎉")
                    st.session_state.correct_answers += 1
                else:
                    st.error(f"Não foi dessa vez. A correta era: {resposta_correta_texto}")
                    st.session_state.incorrect_answers += 1

            if st.session_state.show_feedback:
                if pd.notna(q.get('Comentario_Professor')):
                    st.info(f"**Comentário do Professor:**\n\n{q['Comentario_Professor']}")
                
                if st.button("Próxima Questão ➡️"):
                    st.session_state.current_question_index += 1
                    st.session_state.show_feedback = False
                    st.rerun()
    else:
        st.error("Não conseguimos carregar os dados da planilha. Verifique o link e as colunas.")
