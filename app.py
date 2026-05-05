import streamlit as st
import pandas as pd

# --- Configurações Iniciais ---
st.set_page_config(page_title="Quiz Interativo Pro", page_icon="🧠", layout="wide")

# --- Variáveis de Estado (para manter o estado entre as execuções) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0
if 'incorrect_answers' not in st.session_state:
    st.session_state.incorrect_answers = 0
if 'answers_submitted' not in st.session_state:
    st.session_state.answers_submitted = False
if 'selected_options' not in st.session_state:
    st.session_state.selected_options = {}
if 'filtered_questions' not in st.session_state:
    st.session_state.filtered_questions = pd.DataFrame()

# --- Carregar Dados das Questões (Substitua pelo seu link do Google Sheets CSV) ---
@st.cache_data(ttl=60) # Cache os dados por 1 minuto para facilitar testes
def load_questions():
    # LINK_DO_SEU_CSV_PUBLICO_DA_ABA_QUESTOES_DO_GOOGLE_SHEETS
    csv_url_questions = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBUqPZ49NRGhslCeQ377Ox-5bTzRhDIljonfh_jHYr4Q3YXcs2PI1HuQV9SS4GuNaY3eWEOwSk-DE6/pub?output=csv"
    try:
        df = pd.read_csv(csv_url_questions)
        # Garantir que as colunas essenciais existem
        required_cols = ["ID", "Disciplina", "Enunciado", "A", "B", "C", "D", "E", "Resposta_Correta"]
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Coluna essencial faltante na planilha de questões: {col}")
                return pd.DataFrame()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar as questões: {e}")
        return pd.DataFrame()

# --- Carregar E-mails Autorizados (Substitua pelo seu link do Google Sheets CSV da aba 'usuarios') ---
@st.cache_data(ttl=60)
def load_authorized_emails():
    # LINK_DO_SEU_CSV_PUBLICO_DA_ABA_USUARIOS_DO_GOOGLE_SHEETS
    csv_url_users = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBUqPZ49NRGhslCeQ377Ox-5bTzRhDIljonfh_jHYr4Q3YXcs2PI1HuQV9SS4GuNaY3eWEOwSk-DE6/pub?gid=1423529108&single=true&output=csv" # <-- VOCÊ PRECISA MUDAR ESTE LINK!
    try:
        df_users = pd.read_csv(csv_url_users)
        if 'email' in df_users.columns:
            return [email.strip().lower() for email in df_users['email'].dropna().tolist()]
        else:
            st.warning("Coluna 'email' não encontrada na planilha de usuários. Usando lista padrão.")
            return ["professor@exemplo.com", "aluno@exemplo.com", "teste@teste.com"]
    except Exception as e:
        st.warning(f"Erro ao carregar e-mails de usuários: {e}. Usando lista padrão.")
        return ["professor@exemplo.com", "aluno@exemplo.com", "teste@teste.com"]

questions_df = load_questions()
authorized_emails = load_authorized_emails()

# --- Função de Login ---
def login_page():
    st.title("Questões Odontologia Legal 🚀")
    st.markdown("### Utilize seu email para login.")

    with st.form("login_form"):
        email = st.text_input("Seu e-mail cadastrado:").strip().lower()
        submitted = st.form_submit_button("Entrar")

        if submitted:
            if email in authorized_emails:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.current_page = 0 # Resetar página ao logar
                st.session_state.correct_answers = 0
                st.session_state.incorrect_answers = 0
                st.session_state.answers_submitted = False
                st.session_state.selected_options = {}
                st.rerun()
            else:
                st.error("E-mail não cadastrado ou não autorizado. Por favor, verifique seu e-mail ou entre em contato com o professor.")

# --- Função para exibir questões e coletar respostas ---
def display_questions_page(questions_to_display):
    st.session_state.selected_options = {}
    for idx, q in questions_to_display.iterrows():
        st.markdown(f"**Questão {q['ID']}**")
        st.write(q['Enunciado'])

        if pd.notna(q.get('Link_Imagem')) and str(q['Link_Imagem']).startswith('http'):
            st.image(q['Link_Imagem'], use_column_width=True)

        options = [f"A) {q['A']}", f"B) {q['B']}", f"C) {q['C']}", f"D) {q['D']}", f"E) {q['E']}"]
        
        # Mapeamento de letra para texto da opção
        map_letra = {'A': options[0], 'B': options[1], 'C': options[2], 'D': options[3], 'E': options[4]}
        
        # Usar um key único para cada radio button
        st.session_state.selected_options[q['ID']] = st.radio(
            "Selecione a alternativa correta:",
            options,
            key=f"radio_{q['ID']}_{st.session_state.current_page}",
            index=None
        )
        st.markdown("---")

# --- Função para verificar respostas e dar feedback ---
def check_answers_and_feedback(questions_on_page):
    new_correct = 0
    new_incorrect = 0
    st.session_state.answers_submitted = True

    for idx, q in questions_on_page.iterrows():
        selected_option = st.session_state.selected_options.get(q['ID'])
        
        map_letra = {'A': f"A) {q['A']}", 'B': f"B) {q['B']}", 'C': f"C) {q['C']}", 'D': f"D) {q['D']}", 'E': f"E) {q['E']}"}
        correct_answer_text = map_letra.get(q['Resposta_Correta'].strip().upper())

        st.markdown(f"**Questão {q['ID']}**")
        st.write(q['Enunciado'])

        if selected_option == correct_answer_text:
            st.success(f"✅ Correta! Sua resposta: {selected_option}")
            new_correct += 1
        else:
            st.error(f"❌ Incorreta. Sua resposta: {selected_option if selected_option else 'Nenhuma'}. Correta: {correct_answer_text}")
            new_incorrect += 1
        
        if pd.notna(q.get('Comentario_Professor')) and q['Comentario_Professor']:
            with st.expander(f"Ver Comentário do Professor (Questão {q['ID']})"):
                st.info(q['Comentario_Professor'])
        st.markdown("--- ")
    
    st.session_state.correct_answers += new_correct
    st.session_state.incorrect_answers += new_incorrect

# --- Layout Principal do Aplicativo ---
if not st.session_state.logged_in:
    login_page()
else:
    # Sidebar
    with st.sidebar:
        st.title("Menu do Quiz")
        st.write(f"Olá, **{st.session_state.user_email.split('@')[0].capitalize()}**!")
        if st.button("Sair", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.current_page = 0
            st.session_state.correct_answers = 0
            st.session_state.incorrect_answers = 0
            st.session_state.answers_submitted = False
            st.session_state.selected_options = {}
            st.rerun()
        st.markdown("--- ")

        st.subheader("Filtros")
        if not questions_df.empty:
            disciplines = ["Todas"] + sorted(questions_df["Disciplina"].unique().tolist())
            selected_discipline = st.selectbox("Filtrar por Disciplina:", disciplines, key="discipline_filter")

            if selected_discipline == "Todas":
                st.session_state.filtered_questions = questions_df.copy()
            else:
                st.session_state.filtered_questions = questions_df[questions_df["Disciplina"] == selected_discipline].copy()
            
            # Resetar página e respostas ao mudar o filtro
            if st.session_state.get('last_discipline_filter') != selected_discipline:
                st.session_state.current_page = 0
                st.session_state.answers_submitted = False
                st.session_state.selected_options = {}
                st.session_state.last_discipline_filter = selected_discipline
                st.rerun()

            questions_per_page = st.slider("Questões por página:", min_value=1, max_value=10, value=3, key="q_per_page_slider")
            st.session_state.questions_per_page = questions_per_page
        else:
            st.warning("Nenhuma questão carregada.")
            st.session_state.filtered_questions = pd.DataFrame()

    # Main Content
    st.header("📚 Seu Desempenho")
    col1, col2 = st.columns(2)
    col1.metric(label="Acertos", value=st.session_state.correct_answers)
    col2.metric(label="Erros", value=st.session_state.incorrect_answers)
    st.markdown("--- ")

    if not st.session_state.filtered_questions.empty:
        total_filtered_questions = len(st.session_state.filtered_questions)
        total_pages = (total_filtered_questions + st.session_state.questions_per_page - 1) // st.session_state.questions_per_page

        start_idx = st.session_state.current_page * st.session_state.questions_per_page
        end_idx = min(start_idx + st.session_state.questions_per_page, total_filtered_questions)
        
        questions_on_page = st.session_state.filtered_questions.iloc[start_idx:end_idx].reset_index(drop=True)

        st.subheader(f"Página {st.session_state.current_page + 1} de {total_pages}")

        if not st.session_state.answers_submitted:
            display_questions_page(questions_on_page)
            if st.button("Verificar Respostas desta Página", key="submit_page_answers", disabled=len(st.session_state.selected_options) < len(questions_on_page)):
                check_answers_and_feedback(questions_on_page)
                st.rerun()
        else:
            check_answers_and_feedback(questions_on_page) # Re-exibir feedback após rerun
            
        # Botões de navegação
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("⬅️ Página Anterior", disabled=st.session_state.current_page == 0):
                st.session_state.current_page -= 1
                st.session_state.answers_submitted = False
                st.session_state.selected_options = {}
                st.rerun()
        with nav_col2:
            if st.button("Próxima Página ➡️", disabled=st.session_state.current_page >= total_pages - 1):
                st.session_state.current_page += 1
                st.session_state.answers_submitted = False
                st.session_state.selected_options = {}
                st.rerun()

    else:
        st.info("Nenhuma questão disponível com os filtros selecionados. Por favor, ajuste os filtros ou verifique sua planilha de questões.")
