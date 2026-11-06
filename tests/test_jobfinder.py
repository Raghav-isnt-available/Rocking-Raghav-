import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jobfinder import rank
from jobfinder.location import classify
from jobfinder.models import Job
from jobfinder.profile import Profile
from jobfinder.text import html_to_text, normalize_phrase


class Location(unittest.TestCase):
    def ca(self, loc, **kw):
        p = classify(loc, **kw)
        return p.in_canada or p.remote_open_to_canada

    def test_canadian_cities_and_provinces(self):
        for loc in ["Toronto", "Vancouver, BC (on-site)", "Montréal, Quebec, Canada", "London, ON",
                    "Canada - Remote (ON, AB, BC, or NS Only)", "Remote (Canada)", "Kitchener-Waterloo, ON",
                    "Port Coquitlam, British Columbia", "Toronto, ON, CA"]:
            self.assertTrue(self.ca(loc), loc)

    def test_not_canada(self):
        for loc in ["New Brunswick, NJ", "Amsterdam, NL", "Remote - US: Select locations", "London",
                    "San Francisco, CA", "Anywhere in the United States", "Lima, PE", "Remote UK"]:
            self.assertFalse(self.ca(loc), loc)

    def test_remote_open_regions(self):
        self.assertTrue(classify("Remote - North America", remote_hint=True).remote_open_to_canada)
        self.assertTrue(classify("Remote-NAMER").remote_open_to_canada)
        self.assertTrue(classify("Remote (Worldwide)").remote_open_to_canada)

    def test_multi_location_finds_canadian_part(self):
        p = classify("New York, NY; Toronto, ON")
        self.assertTrue(p.in_canada)
        self.assertEqual(p.city, "toronto")
        self.assertTrue(p.gta)

    def test_secondary_locations_and_hints(self):
        self.assertTrue(classify("London", extra=["Toronto, Ontario, Canada"]).in_canada)
        self.assertTrue(classify("Head office", country_hint="CA").in_canada)


class Levels(unittest.TestCase):
    def test_levels(self):
        cases = {
            "Research Associate": "entry", "Associate Director, Regulatory Affairs": "senior",
            "Associate Product Manager - Network MDM": "entry", "Product Manager": "senior",
            "Intern, Security Analyst - Winter 2027": "intern", "Summer Student, Lab": "intern",
            "QC Analyst II": "mid", "Senior Scientist": "senior", "Scientist": "mid",
            "Pharmacy Assistant": "entry", "Executive Assistant": "entry", "Biologist": "mid",
        }
        for title, want in cases.items():
            self.assertEqual(rank.level_of(title), want, title)


class Text(unittest.TestCase):
    def test_greenhouse_double_escaped_html(self):
        self.assertEqual(html_to_text("&lt;p&gt;Hello &amp;amp; welcome&lt;/p&gt;"), "Hello & welcome")

    def test_years(self):
        self.assertEqual(rank.years_asked("You have 3+ years of industry experience."), 3)
        self.assertEqual(rank.years_asked("Minimum 2-4 years experience in a GMP lab"), 2)
        self.assertIsNone(rank.years_asked("We were founded 10 years ago."))

    def test_phrase_normalization(self):
        self.assertEqual(normalize_phrase("Cell Culture"), "cell culture")

    def test_generic_title_words_barely_count(self):
        self.assertLess(rank._title_score("Shipping Coordinator", ["research coordinator"]), 0.2)
        self.assertEqual(rank._title_score("Research Coordinator, Oncology", ["research coordinator"]), 1.0)
        self.assertAlmostEqual(rank._title_score("Research Technician", ["research coordinator"]), 0.5)


def _profile(**kw):
    base = dict(
        resume_path=Path("x"), companies_path=Path("x"), sectors=[], use_remotive=False, use_adzuna=False,
        min_score=0, max_results=50, preferred_cities=["toronto"], allow_rest_of_canada=True,
        allow_remote=True, titles=["research assistant"], skills=["cell culture", "assay"],
        levels=["intern", "entry", "mid"], max_years_experience=2, exclude_title_words=["software"],
        resume_text="Biochemistry student. Cell culture, ELISA assay development, antibody research.",
    )
    base.update(kw)
    return Profile(**base)


def _job(i, title, location, desc="", days=1, company="Acme Bio"):
    return Job(source="greenhouse", source_id=str(i), company=company, title=title, location=location,
               url=f"https://example.test/{i}", description=desc,
               posted_at=datetime(2026, 11, 6, tzinfo=timezone.utc) - timedelta(days=days))


class Ranking(unittest.TestCase):
    NOW = datetime(2026, 11, 6, tzinfo=timezone.utc)

    def test_filters_and_orders(self):
        jobs = [
            _job(1, "Research Assistant, Antibody Discovery", "Toronto, ON",
                 "Cell culture and ELISA assay work on antibody programs."),
            _job(2, "Research Assistant, Antibody Discovery", "Boston, MA", "Cell culture and assay work."),
            _job(3, "Senior Scientist", "Toronto, ON", "Cell culture assay antibody."),
            _job(4, "Software Engineer", "Toronto, ON", "Python."),
            _job(5, "Marketing Coordinator", "Vancouver, BC", "Brand campaigns and social media."),
            _job(6, "Research Assistant", "Calgary, AB", "Cell culture. Requires 6+ years of lab experience."),
        ]
        out, stats = rank.rank(jobs, _profile(), now=self.NOW)
        titles = [(s.job.source_id, s.score) for s in out]
        ids = [i for i, _ in titles]
        self.assertEqual(ids[0], "1")
        self.assertNotIn("2", ids)  # Boston
        self.assertNotIn("3", ids)  # senior
        self.assertNotIn("4", ids)  # excluded word
        self.assertEqual(stats["not_in_canada"], 1)
        self.assertEqual(stats["wrong_level"], 1)
        self.assertEqual(stats["excluded_title"], 1)
        six = next(s for s in out if s.job.source_id == "6")
        self.assertIn("Asks for 6+ yrs experience", six.flags)
        five = next(s for s in out if s.job.source_id == "5")
        self.assertLess(five.score, six.score)
        self.assertEqual(out[0].matched_skills, ["cell culture", "assay"])

    def test_dedupes_same_title_keeps_toronto(self):
        jobs = [_job(1, "Lab Assistant", "Calgary, AB", "assay"), _job(2, "Lab Assistant", "Toronto, ON", "assay")]
        out, stats = rank.rank(jobs, _profile(), now=self.NOW)
        self.assertEqual([s.job.source_id for s in out], ["2"])
        self.assertEqual(stats["duplicates"], 1)

    def test_preferred_only_when_rest_of_canada_off(self):
        jobs = [_job(1, "Lab Assistant", "Calgary, AB", "assay"), _job(2, "Lab Assistant II", "Toronto, ON", "assay")]
        out, _ = rank.rank(jobs, _profile(allow_rest_of_canada=False), now=self.NOW)
        self.assertEqual([s.job.source_id for s in out], ["2"])


if __name__ == "__main__":
    unittest.main()
