import { Header } from './Header';
import { Footer } from './Footer';

interface LayoutProps {
  children: React.ReactNode;
  wide?: boolean;
}

export function Layout({ children, wide = false }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-mesh-gradient-light dark:bg-mesh-gradient transition-colors duration-200">
      <Header />
      <main className={`flex-1 ${wide ? 'max-w-7xl' : 'max-w-4xl'} w-full mx-auto px-4 py-8`}>
        {children}
      </main>
      <Footer />
    </div>
  );
}
