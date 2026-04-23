"""Servicio de IA basado en Google Gemini para el chat del e-commerce."""

from __future__ import annotations

import asyncio
import os
from typing import Any, Sequence

from src.domain.entities import ChatContext, Product


class GeminiService:
	"""Servicio que construye prompts y genera respuestas con Google Gemini."""

	def __init__(self) -> None:
		"""Configura el cliente de Gemini usando la API key del entorno."""
		self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
		self.model_name = "gemini-2.5-flash"
		self._genai = None
		self._model = None

		if not self.api_key:
			return

		try:
			import google.generativeai as genai

			genai.configure(api_key=self.api_key)
			self._genai = genai
			self._model = genai.GenerativeModel(self.model_name)
		except ImportError:
			self._genai = None
			self._model = None

	async def generate_response(
		self,
		user_message: str,
		products: Sequence[Product],
		context: ChatContext,
	) -> str:
		"""Genera una respuesta contextualizada para el usuario.

		Args:
			user_message (str): Mensaje actual del usuario.
			products (Sequence[Product]): Productos disponibles para recomendar.
			context (ChatContext): Contexto conversacional reciente.

		Returns:
			str: Respuesta generada por Gemini o una respuesta de respaldo.
		"""
		prompt = self._build_prompt(user_message, products, context)

		if self._model is None:
			return self._fallback_response(user_message, products, context)

		try:
			response = await asyncio.to_thread(self._model.generate_content, prompt)
			text = getattr(response, "text", None)
			if text:
				return text.strip()

			return self._fallback_response(user_message, products, context)
		except Exception:
			return self._fallback_response(user_message, products, context)

	def format_products_info(self, products: Sequence[Product]) -> str:
		"""Convierte una lista de productos en un texto legible para el prompt."""
		if not products:
			return "No hay productos disponibles en este momento."

		lines = []
		for product in products:
			lines.append(
				f"- {product.name} | {product.brand} | ${product.price:.2f} | Stock: {product.stock}"
			)
		return "\n".join(lines)

	def _build_prompt(
		self,
		user_message: str,
		products: Sequence[Product],
		context: ChatContext,
	) -> str:
		"""Construye el prompt completo con instrucciones, contexto y productos."""
		products_info = self.format_products_info(products)
		conversation_context = context.format_for_prompt()

		return (
			"Eres un asistente virtual experto en ventas de zapatos para un e-commerce.\n"
			"Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.\n\n"
			"PRODUCTOS DISPONIBLES:\n"
			f"{products_info}\n\n"
			"INSTRUCCIONES:\n"
			"- Sé amigable y profesional\n"
			"- Usa el contexto de la conversación anterior\n"
			"- Recomienda productos específicos cuando sea apropiado\n"
			"- Menciona precios, tallas y disponibilidad\n"
			"- Si no tienes información, sé honesto\n\n"
			"HISTORIAL DE CONVERSACIÓN:\n"
			f"{conversation_context if conversation_context else 'Sin historial previo.'}\n\n"
			f"Usuario: {user_message}\n\n"
			"Asistente:"
		)

	def _fallback_response(
		self,
		user_message: str,
		products: Sequence[Product],
		context: ChatContext,
	) -> str:
		"""Genera una respuesta de respaldo cuando Gemini no está disponible."""
		available_products = [product for product in products if product.is_available()]
		if not available_products:
			return (
				"En este momento no tengo productos disponibles, pero puedo ayudarte a "
				f"afinar tu búsqueda. Me comentaste: '{user_message}'."
			)

		recommendations = ", ".join(
			f"{product.name} ({product.brand}, talla {product.size})"
			for product in available_products[:3]
		)
		context_text = context.format_for_prompt()
		context_note = (
			"" if not context_text else " Tengo en cuenta la conversación anterior para seguir ayudándote."
		)

		return (
			"Puedo recomendarte algunas opciones como "
			f"{recommendations}. {context_note} "
			f"Sobre tu mensaje '{user_message}', dime si buscas talla, color o presupuesto."
		).strip()
