import type { Destination } from '../types'

/**
 * Destination sample data — prices in INR (Indian Rupees).
 *
 * Conversion basis (approximate, rounded to traveller-friendly figures):
 *   1 USD ≈ ₹84  (as of 2024–25; representative rate for prototype)
 *
 * Prices represent estimated all-inclusive starting cost per person
 * (economy return flight from India + 7-night budget stay + basic meals)
 * as a realistic guide for Indian travellers.
 *
 *   Santorini    : ₹1,05,000  (~$1,250 → premium EU island; high flight cost)
 *   Kyoto        : ₹82,000    (~$980  → popular Asia destination; shorter flight)
 *   Machu Picchu : ₹1,22,000  (~$1,450 → long-haul South America + trekking)
 *   Amalfi Coast : ₹92,000    (~$1,100 → Europe; slightly cheaper than Greece)
 *   Bali         : ₹63,000    (~$750  → short-haul Asia; very popular with Indians)
 *   Iceland      : ₹1,51,000  (~$1,800 → premium long-haul; cold-weather gear)
 */
export const destinations: Destination[] = [
  {
    id: '1',
    name: 'Santorini',
    country: 'Greece',
    region: 'Europe',
    image: 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&auto=format&fit=crop&q=80',
    rating: 4.9,
    reviews: 2341,
    endorsements: 8720,
    tags: ['Romantic', 'Scenic', 'Island'],
    description: 'Iconic whitewashed villages perched above the caldera with breathtaking sunsets over the Aegean Sea.',
    priceINR: 105000,
    season: 'Apr – Oct',
    trending: true,
  },
  {
    id: '2',
    name: 'Kyoto',
    country: 'Japan',
    region: 'Asia',
    image: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&auto=format&fit=crop&q=80',
    rating: 4.8,
    reviews: 3102,
    endorsements: 11450,
    tags: ['Cultural', 'Historic', 'Nature'],
    description: 'Ancient temples, bamboo forests and traditional tea houses in Japan\'s timeless cultural capital.',
    priceINR: 82000,
    season: 'Mar – May, Oct – Nov',
    trending: true,
  },
  {
    id: '3',
    name: 'Machu Picchu',
    country: 'Peru',
    region: 'South America',
    image: 'https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=800&auto=format&fit=crop&q=80',
    rating: 4.9,
    reviews: 1890,
    endorsements: 9340,
    tags: ['Adventure', 'Historic', 'Trekking'],
    description: 'The legendary Incan citadel rising from Andean mist — a wonder that takes your breath away.',
    priceINR: 122000,
    season: 'Apr – Oct',
    trending: false,
  },
  {
    id: '4',
    name: 'Amalfi Coast',
    country: 'Italy',
    region: 'Europe',
    image: 'https://images.unsplash.com/photo-1612528443702-f6741f70a049?w=800&auto=format&fit=crop&q=80',
    rating: 4.7,
    reviews: 2756,
    endorsements: 7820,
    tags: ['Scenic', 'Coastal', 'Luxury'],
    description: 'Dramatic cliffside villages, lemon groves and azure waters along Italy\'s most glamorous coastline.',
    priceINR: 92000,
    season: 'May – Sep',
    trending: false,
  },
  {
    id: '5',
    name: 'Bali',
    country: 'Indonesia',
    region: 'Asia',
    image: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&auto=format&fit=crop&q=80',
    rating: 4.6,
    reviews: 4201,
    endorsements: 15300,
    tags: ['Beach', 'Spiritual', 'Culture'],
    description: 'Lush rice terraces, ancient temples and world-class surf breaks on the Island of the Gods.',
    priceINR: 63000,
    season: 'Apr – Sep',
    trending: true,
  },
  {
    id: '6',
    name: 'Iceland',
    country: 'Iceland',
    region: 'Europe',
    image: 'https://images.unsplash.com/photo-1476610182048-b716b8518aae?w=800&auto=format&fit=crop&q=80',
    rating: 4.8,
    reviews: 1623,
    endorsements: 6540,
    tags: ['Adventure', 'Nature', 'Aurora'],
    description: 'Glaciers, geysers, volcanoes and the magical Northern Lights in a land forged by fire and ice.',
    priceINR: 151000,
    season: 'Sep – Mar',
    trending: true,
  },
]

export const regions = ['All', 'Europe', 'Asia', 'Americas', 'Africa', 'Oceania']
