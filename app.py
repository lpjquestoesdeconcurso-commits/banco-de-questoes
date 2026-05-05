import streamlit as st
import pandas as pd

# --- Configurações Iniciais e Estilo ---
st.set_page_config(page_title="Plataforma de Exercícios", layout="wide")

# CSS Personalizado para Paleta Preto e Amarelo
st.markdown("""
    <style>
    /* Fundo principal e textos */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #FFD700;
    }
    
    /* Botões */
    .stButton>button {
        background-color: #FFD700;
        color: #000000;
        border-radius: 5px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #CCAC00;
        color: #000000;
    }
    
    /* Inputs e Radio Buttons */
    .stRadio [data-testid="stWidgetLabel"] p {
        color: #FFD700 !important;
        font-size: 1.1rem;
    }
    
    /* Títulos e Subtítulos */
    h1, h2, h3 {
        color: #FFD700 !important;
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] {
        color: #FFD700 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #222222 !important;
        color: #FFD700 !important;
    }
    
    /* Alertas */
    .stAlert {
        background-color: #111111;
        border: 1px solid #FFD700;
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Variáveis de Estado ---
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
if 'answered_questions' not in st.session_state:
    st.session_state.answered_questions = {} # Armazena feedback por ID de questão

# --- Carregamento de Dados ---
@st.cache_data(ttl=60)
def load_questions():
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBUqPZ49NRGhslCeQ377Ox-5bTzRhDIljonfh_jHYr4Q3YXcs2PI1HuQV9SS4GuNaY3eWEOwSk-DE6/pub?output=csv"
    try:
        df = pd.read_csv(csv_url)
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_authorized_emails():
    # LINK DA SUA ABA DE USUÁRIOS (Ajuste o link abaixo quando tiver o novo)
    csv_url_users = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBUqPZ49NRGhslCeQ377Ox-5bTzRhDIljonfh_jHYr4Q3YXcs2PI1HuQV9SS4GuNaY3eWEOwSk-DE6/pub?output=csv" 
    try:
        df_users = pd.read_csv(csv_url_users)
        if 'email' in df_users.columns:
            return [str(e).strip().lower() for e in df_users['email'].dropna()]
    except:
        pass
    return ["professor@exemplo.com", "teste@teste.com"]

questions_df = load_questions()
authorized_emails = load_authorized_emails()

# --- Navegação ---
def login_page():
    st.title("Acesso ao Sistema")
    with st.container():
        email = st.text_input("E-mail:").strip().lower()
        if st.button("Entrar"):
            if email in authorized_emails or "@" in email: # Permitindo login para teste
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Acesso não autorizado.")

if not st.session_state.logged_in:
    login_page()
else:
    # Sidebar
    st.sidebar.title("Navegação")
    menu = st.sidebar.radio("Ir para:", ["Questões", "Desempenho"])
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()

    if menu == "Questões":
        st.title("Banco de Exercícios")
        
        # Filtros na Sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("Filtros")
        disciplinas = ["Todas"] + sorted(questions_df['Disciplina'].unique().tolist()) if not questions_df.empty else ["Todas"]
        filtro_disc = st.sidebar.selectbox("Disciplina:", disciplinas)
        
        # Lógica de Filtro
        if filtro_disc == "Todas":
            df_final = questions_df
        else:
            df_final = questions_df[questions_df['Disciplina'] == filtro_disc]
        
        # Painel de Status do Filtro
        st.info(f"Filtro Ativo: **{filtro_disc}** | Total de Questões Encontradas: **{len(df_final)}**")
        
        # Paginação
        itens_por_pagina = 5
        total_paginas = (len(df_final) // itens_por_pagina) + (1 if len(df_final) % itens_por_pagina > 0 else 0)
        
        if len(df_final) > 0:
            pagina = st.number_input("Página:", min_value=1, max_value=total_paginas, value=1)
            inicio = (pagina - 1) * itens_por_pagina
            fim = inicio + itens_por_pagina
            questoes_pagina = df_final.iloc[inicio:fim]
            
            for _, q in questoes_pagina.iterrows():
                with st.container():
                    st.markdown(f"### Questão {q['ID']}")
                    st.write(q['Enunciado'])
                    
                    if pd.notna(q.get('Link_Imagem')) and str(q['Link_Imagem']).startswith('http'):
                        st.image(q['Link_Imagem'], use_column_width=True)
                    
                    opcoes = [f"A) {q['A']}", f"B) {q['B']}", f"C) {q['C']}", f"D) {q['D']}", f"E) {q['E']}"]
                    map_correta = {'A': opcoes[0], 'B': opcoes[1], 'C': opcoes[2], 'D': opcoes[3], 'E': opcoes[4]}
                    correta_texto = map_correta.get(q['Resposta_Correta'].strip().upper())
                    
                    # Se já foi respondida nesta sessão, mostra o feedback
                    q_id = str(q['ID'])
                    if q_id in st.session_state.answered_questions:
                        respondida = st.session_state.answered_questions[q_id]
                        st.radio("Sua escolha:", opcoes, index=opcoes.index(respondida['escolha']), key=f"r_{q_id}", disabled=True)
                        if respondida['acertou']:
                            st.success("Resposta Correta")
                        else:
                            st.error(f"Resposta Incorreta. A correta era: {correta_texto}")
                        
                        if pd.notna(q.get('Comentario_Professor')):
                            with st.expander("Comentário do Professor"):
                                st.write(q['Comentario_Professor'])
                    else:
                        # Se não foi respondida, mostra o botão "Responder"
                        escolha = st.radio("Escolha a alternativa:", opcoes, index=None, key=f"r_{q_id}")
                        if st.button("Responder", key=f"btn_{q_id}"):
                            if escolha:
                                acertou = (escolha == correta_texto)
                                st.session_state.answered_questions[q_id] = {'escolha': escolha, 'acertou': acertou}
                                if acertou:
                                    st.session_state.correct_answers += 1
                                else:
                                    st.session_state.incorrect_answers += 1
                                st.rerun()
                            else:
                                st.warning("Selecione uma opção antes de responder.")
                    st.divider()

    elif menu == "Desempenho":
        st.title("Seu Desempenho")
        col1, col2, col3 = st.columns(3)
        
        total = st.session_state.correct_answers + st.session_state.incorrect_answers
        aproveitamento = (st.session_state.correct_answers / total * 100) if total > 0 else 0
        
        col1.metric("Acertos", st.session_state.correct_answers)
        col2.metric("Erros", st.session_state.incorrect_answers)
        col3.metric("Aproveitamento", f"{aproveitamento:.1f}%")
        
        st.markdown("---")
        st.write("Continue praticando para melhorar seus resultados!")
        if st.button("Zerar Estatísticas"):
            st.session_state.correct_answers = 0
            st.session_state.incorrect_answers = 0
            st.session_state.answered_questions = {}
            st.rerun()
