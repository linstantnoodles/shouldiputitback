import unittest 
from models import Filter, FilterList, eval_filter

# Javascript eval
class Tests(unittest.TestCase):
    def test_eval_filter(self):
        f1 = Filter("age", "=", "15") 
        f2 = Filter("age", "=", 15) 
        f3 = Filter("age", "=", True) 
        f4 = Filter("age", "=", False) 
        self.assertEqual(eval_filter(f1), "(age === '15')")
        self.assertEqual(eval_filter(f2), "(age === 15)")
        self.assertEqual(eval_filter(f3), "(age === true)")
        self.assertEqual(eval_filter(f4), "(age === false)")

    def test_eval_not_equals(self):
        f1 = Filter("age", "!=", "15") 
        f2 = Filter("age", "!=", "") 
        self.assertEqual(eval_filter(f1), "(age !== '15')")
        self.assertEqual(eval_filter(f2), "(age !== '')")

    def test_eval_filter_list(self):
        f1 = Filter("age", "=", 15) 
        f2 = Filter("name", "=", "jason") 
        fl1 = FilterList("AND", [f1, f2])
        self.assertEqual(eval_filter(fl1), "((age === 15) && (name === 'jason'))")

    def test_eval_filter_scope(self):
        f1 = Filter("age", "!=", "15") 
        f2 = Filter("age", "!=", "") 
        self.assertEqual(eval_filter(f1, scope="formData"), "(formData.age !== '15')")
        self.assertEqual(eval_filter(f2, scope="formData"), "(formData.age !== '')")

if __name__ == "__main__":
    unittest.main()
