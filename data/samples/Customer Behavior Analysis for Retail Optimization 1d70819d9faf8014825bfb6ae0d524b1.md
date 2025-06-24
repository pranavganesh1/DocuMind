# Customer Behavior Analysis for Retail Optimization

| Name | SRN |
| --- | --- |
| Aaron Thomas Mathew  | PES1UG23AM005 |
| G Pranav Ganesh | PES1UG24AM804 |

### **1. Problem Overview**

Retailers often face difficulty analyzing high-dimensional customer data. This project uses linear algebra to reduce 15 behavioral metrics into 2–3 dimensions for better visualization and targeted marketing, without using ML libraries.

---

### **2. Approach**

The pipeline:

- **Centers** the data for numerical stability,
- Uses **SVD** to find orthogonal directions of maximum variance,
- **Projects** data onto top directions explaining 95% variance,
- **Reconstructs** the original data from the reduced space,
- Calculates **error** to measure information loss.

---

### **3. Dimension Selection**

The number of dimensions `k` is chosen by retaining components that cumulatively explain 95% of the variance. If all data is constant, `k=0` by default.

---

### **4. Relationship Between Spaces**

The reduced subspace consists of linear combinations of the original features, preserving key structure. It simplifies analysis while maintaining interpretability.

---

### **5. Structure Preservation and Edge Cases**

The method preserves geometry (distances/angles) and handles cases like constant features or linearly dependent columns, ensuring stability and reliability.