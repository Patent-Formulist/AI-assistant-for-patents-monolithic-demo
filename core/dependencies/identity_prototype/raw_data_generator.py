from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.dependencies import get_db
from core.dependencies.factories import get_prompt_manager

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


@lru_cache
def get_attribute_matcher():
    from app.service.identity_prototype.raw_data_generator.attribute_matcher import (
        AttributeMatcher,
    )

    return AttributeMatcher()


@lru_cache
def get_response_parser():
    from app.service.identity_prototype.raw_data_generator.response_parser import (
        IdentityResponseParser,
    )

    return IdentityResponseParser()


@lru_cache
def get_dto_builder():
    from app.service.identity_prototype.raw_data_generator.dto_builder import (
        IdentityDtoBuilder,
    )

    return IdentityDtoBuilder(parser=get_response_parser(), matcher=get_attribute_matcher())


@lru_cache
def get_prompt_builder():
    from app.service.identity_prototype.raw_data_generator.prompt_builder import (
        IdentityPrototypePromptBuilder,
    )

    return IdentityPrototypePromptBuilder(prompt_manager=get_prompt_manager())


@lru_cache
def get_identify_prototype():
    from app.service.identity_prototype.raw_data_generator.identify_prototype import (
        IdentityGenerator,
    )
    from core.dependencies.factories import get_llm_client_deepseek

    return IdentityGenerator(
        llm_client=get_llm_client_deepseek(),
        dto_builder=get_dto_builder(),
        prompt_builder=get_prompt_builder(),
    )
