from typing import Literal

from pydantic import BaseModel

type Genre = Literal[
    "All",
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "Film-Noir",
    "Game-Show",
    "History",
    "Horror",
    "Music",
    "Musical",
    "Mystery",
    "News",
    "Reality-TV",
    "Romance",
    "Sci-Fi",
    "Short",
    "Sport",
    "Talk-Show",
    "Thriller",
    "War",
    "Western",
    "Other",
]

type Country = Literal[
    "All",
    "United States",
    "United Kingdom",
    "Korea",
    "Japan",
    "Bangladesh",
    "China",
    "Egypt",
    "France",
    "Germany",
    "India",
    "Indonesia",
    "Iraq",
    "Italy",
    "Ivory Coast",
    "Kenya",
    "Lebanon",
    "Mexico",
    "Morocco",
    "Nigeria",
    "Pakistan",
    "Philippines",
    "Russia",
    "Saudi Arabia",
    "South Africa",
    "Spain",
    "Syria",
    "Thailand",
    "Malaysia",
    "Turkey",
    "Other",
]

type Year = Literal[
    "All",
    "2026",
    "2025",
    "2024",
    "2023",
    "2022",
    "2021",
    "2020",
    "2010s",
    "2000s",
    "1990s",
    "1980s",
    "Other",
]

type Language = Literal[
    "All",
    "English dub",
    "French dub",
    "Hindi dub",
    "Bengali dub",
    "Urdu dub",
    "Punjabi dub",
    "Tamil dub",
    "Telugu dub",
    "Malayalam dub",
    "Kannada dub",
    "Arabic dub",
    "Arabic sub",
    "Tagalog dub",
    "Indonesian dub",
    "Russian dub",
    "Kurdish sub",
    "Spanish dub",
    "Spanish sub",
    "SpanishLatam dub",
]

type SortBy = Literal[
    "ForYou",
    "Hottest",
    "Latest",
    "Rating",
]


class FilterParams(BaseModel):
    genre: Genre = "All"
    country: Country = "All"
    year: Year = "All"
    language: Language = "All"
    sort: SortBy = "ForYou"
