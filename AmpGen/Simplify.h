#ifndef AMPGEN_SIMPLIFY_H
#define AMPGEN_SIMPLIFY_H 1
#include "AmpGen/Expression.h"

namespace AmpGen { 
  class NormalOrderedExpression { 
    public:
      struct Term {
        std::complex<double>      m_prefactor; 
        std::vector<Expression>   m_terms;
        Expression                m_divisor; 
        std::string               m_expressionAsString; 
        bool                      m_markForRemoval;
        void addExpression( const Expression& expression);
        Term( const Expression& expression ) ;
        operator Expression() ;
      };
      void addTerm( const Expression& expression );
      NormalOrderedExpression( const Expression& expression );
      void groupExpressions();

      operator Expression();
      std::vector<Expression> ExpandBrackets( const Expression& expression );
    private:
      std::vector<Term> m_terms; 
  };
}

#endif
