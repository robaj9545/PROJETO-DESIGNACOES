import streamlit as st
import pandas as pd
import io
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


# Caminho para salvar o arquivo CSV
DATABASE_PATH = 'database.csv'
# Senha para acesso à edição
EDIT_PASSWORD = "1234"
# Senha para acesso ao carregamento de dados
LOAD_PASSWORD = "abcd"

# Função para carregar o arquivo de base de dados
def load_data():
    # Solicita a senha para carregar os dados
    load_password = st.text_input("Digite a senha para carregar a base de dados", type="password")
    df = pd.read_csv(DATABASE_PATH)
    st.session_state['df'] = df
    if load_password == LOAD_PASSWORD:
        if os.path.exists(DATABASE_PATH):
            df = pd.read_csv(DATABASE_PATH)
            st.session_state['df'] = df
            st.success('Base de dados carregada do arquivo!')
        else:
            st.warning('Nenhuma base de dados encontrada. Por favor, carregue um arquivo.')

        uploaded_file = st.file_uploader("Escolha um arquivo CSV ou XLSX", type=["csv", "xlsx"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            st.session_state['df'] = df
            st.success('Base de dados carregada com sucesso!')
            df.to_csv(DATABASE_PATH, index=False)  # Salvar a base de dados no arquivo
    elif load_password:
        st.error("Senha incorreta!")

# Função para visualizar dados
def view_data():
    df = pd.read_csv(DATABASE_PATH)
    st.session_state['df'] = df
    if 'df' in st.session_state:
        st.write(st.session_state['df'])
    else:
        st.warning("Por favor, carregue a base de dados na página 'Database'.")

# Função para editar dados
def edit_data():
    # Inicializa a senha se não estiver no estado da sessão
    if 'password_valid' not in st.session_state:
        st.session_state['password_valid'] = False

    # Solicita a senha se não estiver validada
    if not st.session_state['password_valid']:
        password = st.text_input("Digite a senha para editar os dados", type="password")
        if password == EDIT_PASSWORD:
            st.session_state['password_valid'] = True
            st.success("Senha correta! Você pode editar os dados agora.")
            st.rerun()  # Recarrega a página para exibir a interface de edição
        elif password:
            st.error("Senha incorreta!")
        return  # Não prossegue se a senha não estiver validada

    # Se a senha foi validada, exibe a interface de edição
    if 'df' in st.session_state:
        df = st.session_state['df']

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)  # Paginação
        gb.configure_side_bar()  # Barra lateral
        gb.configure_default_column(editable=True)  # Todas as colunas editáveis
        grid_options = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            fit_columns_on_grid_load=True
        )

        edited_df = pd.DataFrame(grid_response['data'])  # Obtém os dados editados

        # Colocar os botões "Salvar" e "Baixar" lado a lado
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Salvar'):
                st.session_state['df'] = edited_df
                edited_df.to_csv(DATABASE_PATH, index=False)  # Salvar as alterações no arquivo
                st.success('Alterações salvas com sucesso!')
        with col2:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                edited_df.to_excel(writer, index=False)
                writer.close()
                buffer.seek(0)

            st.download_button(
                label="Baixar",
                data=buffer,
                file_name="planilha_editada.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("Por favor, carregue a base de dados na página 'Database'.")

# Menu de navegação
st.sidebar.title("Menu")
page = st.sidebar.selectbox("Selecione a página", ["Database", "Designações", "Substituições"])

if page == "Database":
    st.title("Carregar Base de Dados")
    load_data()
elif page == "Designações":
    st.title("DESIGNAÇÕES PARA AS REUNIÕES - JOCKEY CLUB ")
    view_data()
elif page == "Substituições":
    st.title("FAÇA AS SUBSTITUIÇÕES ABAIXO")
    edit_data()
