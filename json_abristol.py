import json


filename = 'two_outputs'
# filename = 'nn_circuit_small'
input_filepath = f"{filename}.json"
output_filepath = f"{filename}.txt"
f = open(input_filepath)
data = json.load(f)

class AGate:
  def __init__(self, id, type, lhs, rhs, out):
    # just a serial id
    self.id = id
    # gate_type: AAdd, AMul
    self.type = type
    # gate's lhs input wire id:
    self.lhs = lhs
    # gate's rhs input wire id:
    self.rhs = rhs
    # gate's output wire id:
    self.out = out

class ANode:
  def __init__(self, id, signals, names, is_const, const_value):
    # 0
    self.id = id
    #
    self.signals = signals
    self.names = names
    self.is_const = is_const
    self.const_value = const_value

anodes = {}
anode_consts = {}
anode_inputs = {}
anode_outputs = {}

for node in data['nodes']:
  node_id = node['id']
  node_signals = node['signals']
  node_names = node['names']
  node_is_const = node['is_const']
  node_const_value = node['const_value']
  anode = ANode(node_id, node_signals, node_names, node_is_const, node_const_value)
  anodes[node_id] = anode
  for node_name in node_names:
    if "0." in node_name:
      anode_inputs[node_id] = node_name[2:]
      anode_outputs[node_id] = node_name[2:]
  if node_is_const:
    anode_consts[node_id] = node_const_value

agates = {}

for gate in data['gates']:
  gate_id = gate['id']
  gate_type = gate['gate_type']
  glh_input = gate['lh_input']
  grh_input = gate['rh_input']
  goutput = gate['output']
  agate = AGate(gate_id, gate_type, glh_input, grh_input, goutput)
  agates[gate_id] = agate

for gid in agates:
  gate = agates[gid]
  lhs = gate.lhs
  rhs = gate.rhs
  out = gate.out
  anode_outputs.pop(lhs, None)
  anode_outputs.pop(rhs, None)
  anode_inputs.pop(out, None)
  if anode_consts.get(lhs) is not None:
    lhs = "("+str(anode_consts[lhs])+")"
  if anode_consts.get(rhs) is not None:
    rhs = "("+str(anode_consts[rhs])+")"
  # if gate.type == 'AAdd':
    # print(""+str(out)+" = "+str(lhs)+" + "+str(rhs))
  # elif gate.type == 'ASub':
    # print(""+str(out)+" = "+str(lhs)+" - "+str(rhs))
  # elif gate.type == 'AMul':
    # print(""+str(out)+" = "+str(lhs)+" * "+str(rhs))
  # elif gate.type == 'ALt':
    # print(""+str(out)+" = "+str(lhs)+" < "+str(rhs))

print("!@# anode_inputs=", anode_inputs)
print("!@# anode_outputs=", anode_outputs)

f.close()

class TNode:
  def __init__(self, rid, type, lnode, rnode):
    self.iid = 0
    self.rid = rid
    self.lnode = lnode
    self.rnode = rnode
    self.type = type
    self.is_root = True
    self.is_leaf = True
    self.is_visited = False

  def visit_dfs(self, id):
    if self.is_visited:
      return id
    self.is_visited = True
    if self.lnode is not None:
      id = self.lnode.visit_dfs(id)
    if self.rnode is not None:
      id = self.rnode.visit_dfs(id)
    self.iid = id
    return id+1

  def visit_root(self):
    if self.is_visited:
      return
    self.is_visited = True
    id = 0
    print(id)
    id = self.lnode.visit_dfs(id)
    id = self.rnode.visit_dfs(id)
    self.iid = id
    print(id)

  def fill_iid_dfs2(self, id):
    if self.is_visited:
      return id
    self.is_visited = True
    if (self.lnode is None) and (self.rnode is None):
      return id
    if self.lnode is not None:
      id = self.lnode.fill_iid_dfs2(id)
    if self.rnode is not None:
      id = self.rnode.fill_iid_dfs2(id)
    self.iid = id
    return id + 1

  def visit_dfs2(self, id):
    if self.is_visited:
      return id
    self.is_visited = True
    if self.lnode is not None:
      id = self.lnode.visit_dfs2(id)
    if self.rnode is not None:
      id = self.rnode.visit_dfs2(id)
    if (self.lnode is None) and (self.rnode is None):
      self.iid = id
      return id + 1
    return id

  def visit_root2(self, tt):
    if self.is_visited:
      return id
    self.is_visited = True
    id = 0
    print(id)
    id = self.lnode.visit_dfs2(id)
    id = self.rnode.visit_dfs2(id)
    tt.reset_visit()
    id = self.fill_iid_dfs2(id)
    print(id)
    return id

  def print_dfs(self, f):
    if self.is_visited:
      return
    self.is_visited = True
    if self.lnode is not None:
      id = self.lnode.print_dfs(f)
    if self.rnode is not None:
      id = self.rnode.print_dfs(f)
    if (self.lnode is None) & (self.rnode is None):
      return
    f.write("2 1 " + str(self.lnode.iid) + " " + str(self.rnode.iid) + " " + str(self.iid) + " " + str(self.type) + "\n")

  def print_root(self, f):
    if self.is_visited:
      return
    self.is_visited = True
    self.lnode.print_dfs(f)
    self.rnode.print_dfs(f)
    f.write("2 1 " + str(self.lnode.iid) + " " + str(self.rnode.iid) + " " + str(self.iid) + " " + str(self.type) + "\n")

class TTree:
  def __init__(self):
    self.roots = None
    self.tnodes = {}
    self.leaves = {}
    self.gcount = 0
    self.wcount = 0

  def insert_node(self, gate):
    gid = gate.id
    gtype = gate.type
    gout = gate.out
    glhs = gate.lhs
    grhs = gate.rhs
    tnode = TNode(gout, gtype, None, None)
    self.tnodes[gout] = tnode
    if (self.tnodes.get(glhs) is None):
      lnode = TNode(glhs, None, None, None)
      self.tnodes[glhs] = lnode
    if (self.tnodes.get(grhs) is None):
      rnode = TNode(grhs, None, None, None)
      self.tnodes[grhs] = rnode

  def reset_visit(self):
    for nid in self.tnodes:
      tnode = self.tnodes[nid]
      tnode.is_visited = False

  def build_tree(self, gates):
    for gid in gates:
      gate = gates[gid]
      self.insert_node(gate)

    for gid in gates:
      gate = gates[gid]
      gout = gate.out
      tnode = self.tnodes[gout]
      glhs = gate.lhs
      grhs = gate.rhs
      lnode = self.tnodes[glhs]
      rnode = self.tnodes[grhs]
      lnode.is_root = False
      rnode.is_root = False
      tnode.is_leaf = False
      tnode.lnode = lnode
      tnode.rnode = rnode
      self.gcount += 1

    for tnid in self.tnodes:
      tnode = self.tnodes[tnid]
      if tnode.is_root:
        self.roots = tnode
      elif tnode.is_leaf:
        self.leaves[tnode.rid] = tnode

    self.wcount = self.roots.visit_root2(self)

  def print_tree(self, f):
    self.roots.print_root(f)

  def leaves_ordered(self):
    ls = {}
    for lid in self.leaves:
      leaf = self.leaves[lid]
      ls[leaf.iid] = leaf
    return ls

tt = TTree()
tt.build_tree(agates)

f = open(output_filepath, "w")
f.write(str(tt.gcount))
f.write(" ")
f.write(str((tt.wcount)))
f.write("\n")
f.write(str(len(tt.leaves)))
f.write(" ")
for i in range(0, len(tt.leaves)):
  f.write("1 ")
f.write("\n")
f.write("1")
f.write(" ")
for i in range(0, 1):
  f.write("1 ")
f.write("\n")
f.write("\n")

tt.reset_visit()
tt.print_tree(f)

# ls = tt.leaves_ordered()

f.close()

# f = open("circ.conf", "w")
# for lid in ls:
#   leaf = ls[lid]
#   f.write(str(lid) + " " + anode_inputs[leaf.rid] + "\n")
# f.close()

# from ast import literal_eval

# fi = open('inputs.json')
# datai = json.load(fi)

# mapi = {}

# for aid in anode_inputs:
#   aname = anode_inputs.get(aid)
#   sep = aname.find("[")
#   access = "datai['"+aname[:sep]+"']"+aname[sep:]
#   mapi[aname] = eval(access)

# for aid in anode_outputs:
#   aname = anode_outputs.get(aid)
#   sep = aname.find("[")
#   access = "datai['"+aname[:sep]+"']"+aname[sep:]
#   mapi[aname] = eval(access)

# print(mapi)

# # Closing file
# fi.close()