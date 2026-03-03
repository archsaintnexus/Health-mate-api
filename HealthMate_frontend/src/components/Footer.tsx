import { Link } from 'react-router-dom'

const links = {
  Product: ['Features', 'Pricing', 'Security', 'Roadmap'],
  Company: ['About', 'Blog', 'Careers', 'Press'],
  Legal: ['Privacy', 'Terms', 'Compliance', 'Contact'],
}

export function Footer() {
  return (
    <footer className="bg-[#0f0f0f] border-t border-[#2d2d2d] py-12">
      <div className="container-max">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="text-2xl font-bold gradient-text mb-2">Health Mate</h3>
            <p className="text-[#a1a1a1] text-sm">Digital healthcare platform for everyone.</p>
          </div>

          {Object.entries(links).map(([category, items]) => (
            <div key={category}>
              <h4 className="font-bold text-white mb-4">{category}</h4>
              <ul className="space-y-2">
                {items.map((item) => (
                  <li key={item}>
                    <a
                      href="#"
                      className="text-[#a1a1a1] hover:text-[#00d4aa] transition-colors text-sm"
                    >
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="border-t border-[#2d2d2d] pt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-[#a1a1a1] text-sm">© 2024 Health Mate. All rights reserved.</p>
          <div className="flex gap-4">
            <a href="#" className="text-[#a1a1a1] hover:text-[#00d4aa] text-sm transition-colors">
              Twitter
            </a>
            <a href="#" className="text-[#a1a1a1] hover:text-[#00d4aa] text-sm transition-colors">
              LinkedIn
            </a>
            <a href="#" className="text-[#a1a1a1] hover:text-[#00d4aa] text-sm transition-colors">
              GitHub
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
