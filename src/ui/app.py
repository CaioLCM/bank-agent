import streamlit as st

import httpx

from src.core.settings import settings

TIMEOUT_SECONDS = 60

st.title("Atendimento Banco Ágil")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "conversation_ended" not in st.session_state:
    st.session_state.conversation_ended = False

def send_message(text: str) -> dict | None:
    """Envia a mensagem para a API. Devolve None quando a chamada falha."""
    try:
        resp = httpx.post(
            f"{settings.api_url}/invoke",
            json={"message": text, "thread_id": st.session_state.thread_id},
            timeout=TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        return resp.json()

    except httpx.ConnectError:
        st.error("Não foi possível falar com o atendimento. Verifique se a API está no ar.")
    except httpx.TimeoutException:
        st.error("O atendimento demorou para responder. Tente enviar novamente.")
    except httpx.HTTPStatusError as error:
        st.error(f"O atendimento respondeu com erro {error.response.status_code}. Tente novamente.")
    except (httpx.HTTPError, ValueError):
        st.error("Houve uma falha inesperada no atendimento. Tente novamente.")

    return None

def render(text: str) -> None:
    """O Streamlit lê $...$ como LaTeX, e valores em reais têm dois cifrões."""
    st.markdown(text.replace("$", r"\$"))

def start_new_conversation() -> None:
    st.session_state.messages = []
    st.session_state.thread_id = None
    st.session_state.conversation_ended = False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        render(message["content"])

if st.session_state.conversation_ended:
    st.info("Atendimento encerrado.")
    st.button("Novo atendimento", on_click=start_new_conversation)

if prompt := st.chat_input("Digite algo", disabled=st.session_state.conversation_ended):
    with st.chat_message("user"):
        render(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if data := send_message(prompt):
        with st.chat_message("assistant"):
            render(data["message"])

        st.session_state.messages.append({"role": "assistant", "content": data["message"]})
        st.session_state.thread_id = data["thread_id"]

        if data["conversation_ended"]:
            st.session_state.conversation_ended = True
            st.rerun()
