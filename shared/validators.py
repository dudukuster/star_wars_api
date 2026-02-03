"""
Validadores Pydantic para parâmetros de entrada

Este módulo define modelos Pydantic para validação automática de parâmetros
de query nos endpoints da API. Garante que os dados de entrada estejam corretos
antes do processamento.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================

class SortOrder(str, Enum):
    """Ordem de ordenação"""
    ASC = "asc"
    DESC = "desc"


class FilmSortBy(str, Enum):
    """Campos disponíveis para ordenação de filmes"""
    TITLE = "title"
    RELEASE_DATE = "release_date"
    EPISODE_ID = "episode_id"


class Gender(str, Enum):
    """Gêneros de personagens"""
    MALE = "male"
    FEMALE = "female"
    NA = "n/a"
    HERMAPHRODITE = "hermaphrodite"


# ============================================================================
# VALIDADORES - FILMES
# ============================================================================

class FilmQueryParams(BaseModel):
    """
    Validador para parâmetros de consulta de filmes

    Parâmetros:
        search: Termo de busca (max 100 caracteres)
        sort_by: Campo para ordenação
        order: Ordem (asc ou desc)
        include_characters: Incluir detalhes completos dos personagens
        include_planets: Incluir detalhes completos dos planetas
        include_species: Incluir detalhes completos das espécies
        include_vehicles: Incluir detalhes completos dos veículos
        include_starships: Incluir detalhes completos das naves
        include_all: Incluir todos os detalhes (sobrescreve outros include_*)
    """
    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Busca por título do filme"
    )
    sort_by: Optional[FilmSortBy] = Field(
        FilmSortBy.RELEASE_DATE,
        description="Campo para ordenação"
    )
    order: Optional[SortOrder] = Field(
        SortOrder.ASC,
        description="Ordem de ordenação (asc ou desc)"
    )
    include_characters: Optional[bool] = Field(
        False,
        description="Incluir detalhes completos dos personagens do filme"
    )
    include_planets: Optional[bool] = Field(
        False,
        description="Incluir detalhes completos dos planetas do filme"
    )
    include_species: Optional[bool] = Field(
        False,
        description="Incluir detalhes completas das espécies do filme"
    )
    include_vehicles: Optional[bool] = Field(
        False,
        description="Incluir detalhes completos dos veículos do filme"
    )
    include_starships: Optional[bool] = Field(
        False,
        description="Incluir detalhes completos das naves do filme"
    )
    include_all: Optional[bool] = Field(
        False,
        description="Incluir TODOS os detalhes relacionados (characters, planets, species, vehicles, starships)"
    )

    class Config:
        use_enum_values = True


# ============================================================================
# VALIDADORES - PERSONAGENS
# ============================================================================

class CharacterQueryParams(BaseModel):
    """
    Validador para parâmetros de consulta de personagens

    Parâmetros:
        search: Termo de busca (max 100 caracteres)
        page: Número da página (1-100)
        gender: Filtro por gênero
        include_films: Incluir detalhes dos filmes
        include_homeworld: Incluir detalhes do planeta de origem
        include_species: Incluir detalhes das espécies
        include_vehicles: Incluir detalhes dos veículos
        include_starships: Incluir detalhes das naves
        include_all: Incluir todos os detalhes (sobrescreve outros include_*)
    """
    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Busca por nome do personagem"
    )
    page: Optional[int] = Field(
        1,
        ge=1,
        le=100,
        description="Número da página (1-100)"
    )
    gender: Optional[Gender] = Field(
        None,
        description="Filtro por gênero"
    )
    include_films: Optional[bool] = Field(
        False,
        description="Incluir detalhes dos filmes em que o personagem aparece"
    )
    include_homeworld: Optional[bool] = Field(
        False,
        description="Incluir detalhes do planeta de origem (homeworld)"
    )
    include_species: Optional[bool] = Field(
        False,
        description="Incluir detalhes das espécies do personagem"
    )
    include_vehicles: Optional[bool] = Field(
        False,
        description="Incluir detalhes dos veículos pilotados"
    )
    include_starships: Optional[bool] = Field(
        False,
        description="Incluir detalhes das naves pilotadas"
    )
    include_all: Optional[bool] = Field(
        False,
        description="Incluir TODOS os detalhes relacionados (films, homeworld, species, vehicles, starships)"
    )

    class Config:
        use_enum_values = True


# ============================================================================
# VALIDADORES - PLANETAS
# ============================================================================

class PlanetQueryParams(BaseModel):
    """
    Validador para parâmetros de consulta de planetas

    Parâmetros:
        search: Termo de busca (max 100 caracteres)
        page: Número da página (1-100)
        climate: Filtro por clima
        terrain: Filtro por terreno
        include_residents: Incluir detalhes dos residentes
        include_films: Incluir detalhes dos filmes
        include_all: Incluir todos os detalhes
    """
    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Busca por nome do planeta"
    )
    page: Optional[int] = Field(
        1,
        ge=1,
        le=100,
        description="Número da página (1-100)"
    )
    climate: Optional[str] = Field(
        None,
        max_length=50,
        description="Filtro por clima (ex: arid, temperate)"
    )
    terrain: Optional[str] = Field(
        None,
        max_length=50,
        description="Filtro por terreno (ex: desert, grasslands)"
    )
    include_residents: Optional[bool] = Field(
        False,
        description="Incluir detalhes completos dos residentes do planeta"
    )
    include_films: Optional[bool] = Field(
        False,
        description="Incluir detalhes completos dos filmes onde o planeta aparece"
    )
    include_all: Optional[bool] = Field(
        False,
        description="Incluir TODOS os detalhes relacionados (residents, films)"
    )

    @field_validator('climate', 'terrain')
    @classmethod
    def lowercase_filter(cls, v: Optional[str]) -> Optional[str]:
        """Converte filtros para lowercase para comparação consistente"""
        return v.lower() if v else None


# ============================================================================
# VALIDADORES - NAVES
# ============================================================================

class StarshipQueryParams(BaseModel):
    """
    Validador para parâmetros de consulta de naves espaciais

    Parâmetros:
        search: Termo de busca (max 100 caracteres)
        page: Número da página (1-100)
        starship_class: Filtro por classe da nave
        manufacturer: Filtro por fabricante
    """
    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Busca por nome da nave"
    )
    page: Optional[int] = Field(
        1,
        ge=1,
        le=100,
        description="Número da página (1-100)"
    )
    starship_class: Optional[str] = Field(
        None,
        max_length=50,
        description="Filtro por classe da nave (ex: Starfighter, Corvette)"
    )
    manufacturer: Optional[str] = Field(
        None,
        max_length=100,
        description="Filtro por fabricante"
    )

    @field_validator('starship_class', 'manufacturer')
    @classmethod
    def lowercase_filter(cls, v: Optional[str]) -> Optional[str]:
        """Converte filtros para lowercase para comparação consistente"""
        return v.lower() if v else None
