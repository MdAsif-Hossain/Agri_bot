"""
Tests for the Knowledge Graph schema, entity linker, and seed data.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agribot.knowledge_graph.schema import KnowledgeGraph
from agribot.knowledge_graph.seed_data import seed_knowledge_graph
from agribot.knowledge_graph.entity_linker import EntityLinker


@pytest.fixture
def kg(tmp_path):
    """Create a fresh KG in a temp directory."""
    db_path = tmp_path / "test_kg.db"
    kg = KnowledgeGraph(db_path)
    yield kg
    kg.close()


@pytest.fixture
def seeded_kg(kg):
    """KG with seed data loaded."""
    seed_knowledge_graph(kg)
    return kg


class TestKnowledgeGraphSchema:
    """Tests for KG CRUD operations."""

    def test_add_entity(self, kg):
        eid = kg.add_entity("ধান", "Rice", "crop")
        assert eid > 0

    def test_get_entity(self, kg):
        eid = kg.add_entity("ধান", "Rice", "crop")
        entity = kg.get_entity(eid)
        assert entity is not None
        assert entity.canonical_en == "Rice"
        assert entity.canonical_bn == "ধান"
        assert entity.entity_type == "crop"

    def test_add_alias(self, kg):
        eid = kg.add_entity("ধান", "Rice", "crop")
        aid = kg.add_alias(eid, "paddy", "english")
        assert aid > 0

    def test_find_by_alias(self, kg):
        eid = kg.add_entity("ধান", "Rice", "crop")
        kg.add_alias(eid, "paddy", "english")
        results = kg.find_by_alias("paddy")
        assert len(results) == 1
        assert results[0].canonical_en == "Rice"

    def test_find_by_alias_case_insensitive(self, kg):
        eid = kg.add_entity("ধান", "Rice", "crop")
        kg.add_alias(eid, "Paddy", "english")
        results = kg.find_by_alias("paddy")
        assert len(results) == 1

    def test_find_by_partial_alias(self, kg):
        eid = kg.add_entity("ধান", "Rice", "crop")
        kg.add_alias(eid, "paddy rice", "english")
        results = kg.find_by_partial_alias("paddy")
        assert len(results) >= 1

    def test_add_relation(self, kg):
        e1 = kg.add_entity("পাতায় দাগ", "Leaf Spots", "symptom")
        e2 = kg.add_entity("ব্লাস্ট রোগ", "Rice Blast", "disease")
        kg.add_relation(e1, "symptom_of", e2, "test")
        # Should not raise

    def test_get_neighbors(self, kg):
        e1 = kg.add_entity("পাতায় দাগ", "Leaf Spots", "symptom")
        e2 = kg.add_entity("ব্লাস্ট রোগ", "Rice Blast", "disease")
        kg.add_relation(e1, "symptom_of", e2, "test")
        neighbors = kg.get_neighbors(e1, hops=1)
        assert len(neighbors) == 1
        assert neighbors[0][0].canonical_en == "Rice Blast"
        assert neighbors[0][1] == "symptom_of"

    def test_get_stats(self, kg):
        kg.add_entity("ধান", "Rice", "crop")
        stats = kg.get_stats()
        assert stats["entities"] >= 1
        assert "aliases" in stats
        assert "relations" in stats

    def test_get_nonexistent_entity(self, kg):
        result = kg.get_entity(99999)
        assert result is None


class TestSeedData:
    """Tests for KG seed data."""

    def test_seed_loads(self, seeded_kg):
        stats = seeded_kg.get_stats()
        assert stats["entities"] > 10
        assert stats["aliases"] > 20
        assert stats["relations"] > 5

    def test_seed_idempotent(self, seeded_kg):
        """Seeding twice should not duplicate data."""
        stats_before = seeded_kg.get_stats()
        seed_knowledge_graph(seeded_kg)
        stats_after = seeded_kg.get_stats()
        assert stats_before["entities"] == stats_after["entities"]

    def test_rice_entity_exists(self, seeded_kg):
        results = seeded_kg.find_by_alias("rice")
        assert any(e.canonical_en == "Rice" for e in results)

    def test_blast_entity_exists(self, seeded_kg):
        results = seeded_kg.find_by_alias("blast")
        assert any(e.canonical_en == "Rice Blast" for e in results)

    def test_dialect_alias_exists(self, seeded_kg):
        """Colloquial/dialect terms should be present."""
        results = seeded_kg.find_by_alias("পাতা পোড়া")
        assert len(results) >= 1  # Should find Rice Blast


class TestEntityLinker:
    """Tests for entity linking and query expansion."""

    def test_link_entities_english(self, seeded_kg):
        linker = EntityLinker(seeded_kg)
        entities = linker.link_entities("rice blast treatment")
        names = [e.canonical_en for e in entities]
        assert "Rice" in names or "Rice Blast" in names

    def test_link_entities_bengali(self, seeded_kg):
        linker = EntityLinker(seeded_kg)
        entities = linker.link_entities("ধান ব্লাস্ট")
        assert len(entities) >= 1

    def test_expand_query(self, seeded_kg):
        linker = EntityLinker(seeded_kg)
        original = "rice blast"
        expanded = linker.expand_query(original)
        # Expanded query should be at least as long as original
        assert len(expanded) >= len(original)

    def test_expand_query_no_match(self, seeded_kg):
        linker = EntityLinker(seeded_kg)
        original = "xyznonexistent query"
        expanded = linker.expand_query(original)
        assert expanded == original  # Should return original unchanged

    def test_link_empty_query(self, seeded_kg):
        linker = EntityLinker(seeded_kg)
        entities = linker.link_entities("")
        assert entities == []
