import { useState } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import DestinationsSection from './components/DestinationsSection'
import HowItWorks from './components/HowItWorks'
import About from './components/About'
import CallToAction from './components/CallToAction'
import Footer from './components/Footer'

function App() {
  const [searchQuery, setSearchQuery] = useState<string>('')

  return (
    <div className="min-h-screen">
      <Navbar />
      <main>
        <Hero onSearch={setSearchQuery} />
        <DestinationsSection
          searchQuery={searchQuery}
          onClearSearch={() => setSearchQuery('')}
        />
        <HowItWorks />
        <About />
        <CallToAction />
      </main>
      <Footer />
    </div>
  )
}

export default App
