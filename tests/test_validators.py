"""
Testes para os validadores Pydantic

Testa validação de parâmetros de entrada para todos os endpoints,
incluindo limites, tipos e enums.
"""

import pytest
from pydantic import ValidationError
from validators import (
    CharacterQueryParams,
    FilmQueryParams,
    PlanetQueryParams,
    StarshipQueryParams,
    Gender,
    FilmSortBy,
    SortOrder
)


class TestCharacterQueryParams:
    """Testes para validador de parâmetros de personagens"""

    def test_valid_params(self):
        """Testa parâmetros válidos"""
        params = CharacterQueryParams(
            search="luke",
            page=1,
            gender="male",
            include_films=True
        )
        assert params.search == "luke"
        assert params.page == 1
        assert params.gender == "male"
        assert params.include_films is True

    def test_default_values(self):
        """Testa valores padrão"""
        params = CharacterQueryParams()
        assert params.search is None
        assert params.page == 1
        assert params.gender is None
        assert params.include_films is False
        assert params.include_all is False

    def test_page_validation_min(self):
        """Testa validação de página mínima"""
        with pytest.raises(ValidationError) as exc_info:
            CharacterQueryParams(page=0)
        assert "greater_than_equal" in str(exc_info.value)

    def test_page_validation_max(self):
        """Testa validação de página máxima"""
        with pytest.raises(ValidationError) as exc_info:
            CharacterQueryParams(page=101)
        assert "less_than_equal" in str(exc_info.value)

    def test_search_max_length(self):
        """Testa validação de tamanho máximo de search"""
        with pytest.raises(ValidationError) as exc_info:
            CharacterQueryParams(search="a" * 101)
        assert "string_too_long" in str(exc_info.value)

    def test_gender_enum_valid(self):
        """Testa valores válidos do enum Gender"""
        for gender in ["male", "female", "n/a", "hermaphrodite"]:
            params = CharacterQueryParams(gender=gender)
            assert params.gender == gender

    def test_gender_enum_invalid(self):
        """Testa valor inválido do enum Gender"""
        with pytest.raises(ValidationError) as exc_info:
            CharacterQueryParams(gender="alien")
        assert "enum" in str(exc_info.value).lower()

    def test_boolean_fields(self):
        """Testa campos booleanos"""
        params = CharacterQueryParams(
            include_films=True,
            include_homeworld=True,
            include_species=True,
            include_vehicles=True,
            include_starships=True,
            include_all=True
        )
        assert params.include_films is True
        assert params.include_homeworld is True
        assert params.include_species is True
        assert params.include_vehicles is True
        assert params.include_starships is True
        assert params.include_all is True


class TestFilmQueryParams:
    """Testes para validador de parâmetros de filmes"""

    def test_valid_params(self):
        """Testa parâmetros válidos"""
        params = FilmQueryParams(
            search="empire",
            sort_by="title",
            order="asc"
        )
        assert params.search == "empire"
        assert params.sort_by == "title"
        assert params.order == "asc"

    def test_default_values(self):
        """Testa valores padrão"""
        params = FilmQueryParams()
        assert params.search is None
        assert params.sort_by == "release_date"
        assert params.order == "asc"
        assert params.include_characters is False
        assert params.include_all is False

    def test_sort_by_enum_valid(self):
        """Testa valores válidos do enum sort_by"""
        for sort_field in ["title", "release_date", "episode_id"]:
            params = FilmQueryParams(sort_by=sort_field)
            assert params.sort_by == sort_field

    def test_order_enum_valid(self):
        """Testa valores válidos do enum order"""
        for order in ["asc", "desc"]:
            params = FilmQueryParams(order=order)
            assert params.order == order

    def test_search_max_length(self):
        """Testa validação de tamanho máximo de search"""
        with pytest.raises(ValidationError) as exc_info:
            FilmQueryParams(search="x" * 101)
        assert "string_too_long" in str(exc_info.value)

    def test_include_fields(self):
        """Testa campos include"""
        params = FilmQueryParams(
            include_characters=True,
            include_planets=True,
            include_species=True,
            include_vehicles=True,
            include_starships=True,
            include_all=True
        )
        assert params.include_characters is True
        assert params.include_planets is True
        assert params.include_species is True
        assert params.include_vehicles is True
        assert params.include_starships is True
        assert params.include_all is True


class TestPlanetQueryParams:
    """Testes para validador de parâmetros de planetas"""

    def test_valid_params(self):
        """Testa parâmetros válidos"""
        params = PlanetQueryParams(
            search="tatooine",
            page=2,
            climate="arid",
            terrain="desert"
        )
        assert params.search == "tatooine"
        assert params.page == 2
        assert params.climate == "arid"
        assert params.terrain == "desert"

    def test_default_values(self):
        """Testa valores padrão"""
        params = PlanetQueryParams()
        assert params.search is None
        assert params.page == 1
        assert params.climate is None
        assert params.terrain is None
        assert params.include_residents is False
        assert params.include_films is False

    def test_page_validation(self):
        """Testa validação de página"""
        with pytest.raises(ValidationError):
            PlanetQueryParams(page=0)
        with pytest.raises(ValidationError):
            PlanetQueryParams(page=101)

    def test_lowercase_filter_climate(self):
        """Testa conversão para lowercase no climate"""
        params = PlanetQueryParams(climate="ARID")
        assert params.climate == "arid"

    def test_lowercase_filter_terrain(self):
        """Testa conversão para lowercase no terrain"""
        params = PlanetQueryParams(terrain="DESERT")
        assert params.terrain == "desert"

    def test_search_max_length(self):
        """Testa validação de tamanho máximo de search"""
        with pytest.raises(ValidationError) as exc_info:
            PlanetQueryParams(search="t" * 101)
        assert "string_too_long" in str(exc_info.value)

    def test_include_fields(self):
        """Testa campos include"""
        params = PlanetQueryParams(
            include_residents=True,
            include_films=True,
            include_all=True
        )
        assert params.include_residents is True
        assert params.include_films is True
        assert params.include_all is True


class TestStarshipQueryParams:
    """Testes para validador de parâmetros de naves"""

    def test_valid_params(self):
        """Testa parâmetros válidos"""
        params = StarshipQueryParams(
            search="falcon",
            page=1,
            starship_class="light freighter",
            manufacturer="corellian"
        )
        assert params.search == "falcon"
        assert params.page == 1
        assert params.starship_class == "light freighter"
        assert params.manufacturer == "corellian"

    def test_default_values(self):
        """Testa valores padrão"""
        params = StarshipQueryParams()
        assert params.search is None
        assert params.page == 1
        assert params.starship_class is None
        assert params.manufacturer is None
        assert params.include_pilots is False
        assert params.include_films is False

    def test_page_validation(self):
        """Testa validação de página"""
        with pytest.raises(ValidationError):
            StarshipQueryParams(page=-1)
        with pytest.raises(ValidationError):
            StarshipQueryParams(page=150)

    def test_lowercase_filter_starship_class(self):
        """Testa conversão para lowercase no starship_class"""
        params = StarshipQueryParams(starship_class="STARFIGHTER")
        assert params.starship_class == "starfighter"

    def test_lowercase_filter_manufacturer(self):
        """Testa conversão para lowercase no manufacturer"""
        params = StarshipQueryParams(manufacturer="KUAT DRIVE YARDS")
        assert params.manufacturer == "kuat drive yards"

    def test_search_max_length(self):
        """Testa validação de tamanho máximo de search"""
        with pytest.raises(ValidationError) as exc_info:
            StarshipQueryParams(search="f" * 101)
        assert "string_too_long" in str(exc_info.value)

    def test_include_fields(self):
        """Testa campos include"""
        params = StarshipQueryParams(
            include_pilots=True,
            include_films=True,
            include_all=True
        )
        assert params.include_pilots is True
        assert params.include_films is True
        assert params.include_all is True


class TestEnums:
    """Testes para os enums"""

    def test_gender_enum_values(self):
        """Testa valores do enum Gender"""
        assert Gender.MALE.value == "male"
        assert Gender.FEMALE.value == "female"
        assert Gender.NA.value == "n/a"
        assert Gender.HERMAPHRODITE.value == "hermaphrodite"

    def test_film_sort_by_enum_values(self):
        """Testa valores do enum FilmSortBy"""
        assert FilmSortBy.TITLE.value == "title"
        assert FilmSortBy.RELEASE_DATE.value == "release_date"
        assert FilmSortBy.EPISODE_ID.value == "episode_id"

    def test_sort_order_enum_values(self):
        """Testa valores do enum SortOrder"""
        assert SortOrder.ASC.value == "asc"
        assert SortOrder.DESC.value == "desc"
