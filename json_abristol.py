import json


# filename = 'two_outputs'
filename = 'nn_circuit_small'
# filename = 'circ'
# filename = 'arith_circuit_example'
input_filepath = f"{filename}.json"
output_filepath = f"{filename}.txt"
node_id_to_wire_index_filepath = f"{filename}.node_id_to_wire_index.json"
with open(input_filepath) as f:
  data = json.load(f)

class AGate:
  def __init__(self, id: int, type: str, lhs: int, rhs: int, out: int):
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
  def __init__(self, id: int, signals: list[int], names: list[str], is_const: bool, const_value: int):
    # TODO: ?
    self.id = id
    # not used
    self.signals = signals
    # wire names
    self.names = names
    # is wire a constant
    self.is_const = is_const
    # if wire is a constant, this is the value
    self.const_value = const_value


# node_id -> ANode
anodes: dict[int, ANode] = {}
# node_id -> const_value
anode_consts: dict[int, int] = {}
# node_id -> wire_name
anode_inputs: dict[int, str] = {}
# node_id -> wire_name
anode_outputs: dict[int, str] = {}


# Parse the json file
for node in data['nodes']:
  node_id = node['id']
  node_signals = node['signals']
  node_names = node['names']
  node_is_const = node['is_const']
  node_const_value = node['const_value']
  anode = ANode(node_id, node_signals, node_names, node_is_const, node_const_value)
  anodes[node_id] = anode
  # Should just use the last one?
  for node_name in node_names:
    if "0." in node_name:
      anode_inputs[node_id] = node_name[2:]
      anode_outputs[node_id] = node_name[2:]
  if node_is_const:
    anode_consts[node_id] = node_const_value

agates: dict[int, AGate] = {}

for gate in data['gates']:
  gate_id = gate['id']
  gate_type = gate['gate_type']
  glh_input = gate['lh_input']
  grh_input = gate['rh_input']
  goutput = gate['output']
  agate = AGate(gate_id, gate_type, glh_input, grh_input, goutput)
  agates[gate_id] = agate

# print("!@# before pop: anode_inputs=", anode_inputs)
# print("!@# before pop: anode_outputs=", anode_outputs)


# Clean up `anode_inputs` and `anode_outputs` to make sure they only contain their corresponding wires
# gid = 0...ngate-1
for gid in agates:
  gate = agates[gid]
  lhs = gate.lhs
  rhs = gate.rhs
  out = gate.out
  # Remove lhs input from `anode_outputs`
  print("!@# anode_outputs.pop(lhs)=", anode_outputs.pop(lhs, None))
  # Remove rhs input from `anode_outputs`
  print("!@# anode_outputs.pop(rhs)=", anode_outputs.pop(rhs, None))
  # Remove output from `anode_inputs`
  print("!@# anode_inputs.pop(out)=", anode_inputs.pop(out, None))
  # Handle constants
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

print("!@# after pop: anode_inputs= ", anode_inputs)
print("!@# after pop: anode_outputs=", anode_outputs)
print("!@# after pop: anode_consts= ", anode_consts)


# Wires?
class TNode:
  def __init__(self, rid: int, type: str | None, lnode: 'TNode', rnode: 'TNode'):
    self.iid = 0
    # real id?
    self.rid = rid
    self.lnode = lnode
    self.rnode = rnode
    # gate type. if it's a wire, it's None
    self.type = type
    self.is_root = True
    self.is_leaf = True
    self.is_visited = False

  def visit_dfs(self, id: int) -> int:
    if self.is_visited:
      return id
    self.is_visited = True
    if self.lnode is not None:
      id = self.lnode.visit_dfs(id)
    if self.rnode is not None:
      id = self.rnode.visit_dfs(id)
    self.iid = id
    return id + 1

  def fill_iid_dfs2(self, id: int) -> int:
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

  def visit_dfs2(self, id: int) -> int:
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

  def visit_root2(self, tt: 'TTree') -> int:
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
    if (self.lnode is None) and (self.rnode is None):
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
    self.roots: list[TNode] = []
    # node_id -> TNode. All nodes wires
    self.tnodes: dict[int, TNode] = {}
    self.leaves: dict[int, TNode] = {}
    self.gcount = 0
    self.wcount = 0

  def insert_node(self, gate: AGate):
    gtype = gate.type
    gout = gate.out
    # left wire
    glhs = gate.lhs
    # right wire
    grhs = gate.rhs
    # TNode(rid, type, lnode, rnode)
    tnode = TNode(gout, gtype, None, None)
    self.tnodes[gout] = tnode
    # if left wire is not in the tree, create a new node for it
    if (self.tnodes.get(glhs) is None):
      # wire
      lnode = TNode(glhs, None, None, None)
      self.tnodes[glhs] = lnode
    # if right wire is not in the tree, create a new node for it
    if (self.tnodes.get(grhs) is None):
      rnode = TNode(grhs, None, None, None)
      self.tnodes[grhs] = rnode

  def reset_visit(self):
    for nid in self.tnodes:
      tnode = self.tnodes[nid]
      tnode.is_visited = False

  def build_tree(self, gates: dict[int, AGate]):
    # `gates` is ordered by id.
    # Insert all wires into self.tnodes
    for gid in gates:
      gate = gates[gid]
      self.insert_node(gate)

    # for each gate, set input wires as children of the output wire
    # also, count gates `self.gcount` and wires `self.wcount`
    for gid in gates:
      gate = gates[gid]
      gout = gate.out
      # output node
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

    # If a node is a root, add it to `self.roots`
    # If a node is a leaf, add it to `self.leaves`
    for tnid in self.tnodes:
      tnode = self.tnodes[tnid]
      assert tnode.rid == tnid
      if tnode.is_root:
        self.roots.append(tnode)
      elif tnode.is_leaf:
        self.leaves[tnid] = tnode

    self.topological_sort_nodes()
    self.wcount = len(self.sorted_wires)

  def topological_sort_nodes(self):
    # Count how many wires a node is pointed to
    pointed_to = {}
    for nid in self.tnodes:
      pointed_to[nid] = 0
    for nid in self.tnodes:
      tnode = self.tnodes[nid]
      if tnode.lnode:
        pointed_to[tnode.lnode.rid] += 1
      if tnode.rnode:
        pointed_to[tnode.rnode.rid] += 1
    print("!@# before: pointed_to=", pointed_to)
    # Start from the known roots (outputs)
    reversed_roots = self.roots[::-1]
    for i in reversed_roots:
      pointed_to.pop(i.rid)
    print("!@# after:  pointed_to=", pointed_to)
    queue = list(reversed_roots)
    print("!@# queue before while=", queue)
    wires: list[TNode] = []
    wire_index = 0
    while queue:
      # Visit next node
      current_node = queue.pop(0)
      # print("")
      # print("")
      # print("!@# loop i=", wire_index, ": visit current_node.rid=", current_node.rid)
      # print("!@# loop i=", wire_index, ": queue before decrement=", [i.rid for i in queue])
      # print("!@# loop i=", wire_index, ": pointed_to before decrement=", pointed_to)
      current_node.iid = wire_index
      wires.append(current_node)
      # Decrement the count of the nodes it points to
      if current_node.lnode is not None:
        if pointed_to[current_node.lnode.rid] <= 0:
          raise Exception("pointed_to <= 0")
        pointed_to[current_node.lnode.rid] -= 1
        # If the count is 0, add it to the queue and delete it from `pointed_to`
        if pointed_to[current_node.lnode.rid] == 0:
          queue.append(current_node.lnode)
          pointed_to.pop(current_node.lnode.rid)
        elif pointed_to[current_node.lnode.rid] < 0:
          raise Exception("pointed_to < 0")
      if current_node.rnode is not None:
        if pointed_to[current_node.rnode.rid] <= 0:
          raise Exception("pointed_to <= 0")
        pointed_to[current_node.rnode.rid] -= 1
        # If the count is 0, add it to the queue and delete it from `pointed_to`
        if pointed_to[current_node.rnode.rid] == 0:
          queue.append(current_node.rnode)
          pointed_to.pop(current_node.rnode.rid)
        elif pointed_to[current_node.rnode.rid] < 0:
          raise Exception("pointed_to < 0")
      # print("!@# loop i=", wire_index, ": queue after decrement=", [i.rid for i in queue])
      # print("!@# loop i=", wire_index, ": pointed_to after decrement=", pointed_to)
      wire_index += 1
    # Now wires contains all nodes in topological order, i.e. every parent (output) has lower index
    # than their children (inputs). Since we want inputs having lower values than outputs, reverse the list
    self.sorted_wires = wires[::-1]
    for index, node in enumerate(self.sorted_wires):
      node.iid = index
    # self.map_node_rid_to_wire_index = {i.rid: index for index, i in enumerate(self.sorted_wires)}

  def print_tree(self, f):
    # for root in self.roots:
    #   root.print_dfs(f)
    # print("!@# sorted_wires=", [i.rid for i in self.sorted_wires])
    # map_node_rid_to_wire_index = {i.rid: index for index, i in enumerate(self.sorted_wires)}
    # print("!@# map_node_rid_to_wire_index=", map_node_rid_to_wire_index)
    for node in self.sorted_wires:
      # Should check gate type instead?
      if node.type is None:
        # Sanity check
        assert node.lnode is None and node.rnode is None
        continue
      # lnode_iid = map_node_rid_to_wire_index[node.lnode.rid]
      # rnode_iid = map_node_rid_to_wire_index[node.rnode.rid]
      # output_iid = map_node_rid_to_wire_index[node.rid]
      # f.write("2 1 " + str(lnode_iid) + " " + str(rnode_iid) + " " + str(output_iid) + " " + str(node.type) + "\n")
      f.write("2 1 " + str(node.lnode.iid) + " " + str(node.rnode.iid) + " " + str(node.iid) + " " + str(node.type) + "\n")

  def leaves_ordered(self):
    ls = {}
    for lid in self.leaves:
      leaf = self.leaves[lid]
      ls[leaf.iid] = leaf
    return ls

tt = TTree()
tt.build_tree(agates)

with open(output_filepath, "w") as f:
  # num gates and wires
  f.write(str(tt.gcount))
  f.write(" ")
  f.write(str((tt.wcount)))
  f.write("\n")
  # num inputs
  num_inputs = len(tt.leaves)
  f.write(f"{num_inputs} " + " ".join(["1"] * num_inputs) + "\n")
  # num outputs
  num_outputs = len(tt.roots)
  f.write(f"{num_outputs} " + " ".join(["1"] * num_outputs) + "\n")

  f.write("\n")

  tt.reset_visit()
  # print a line for each gate
  tt.print_tree(f)


# Output wire_index -> node_id
# Output the wire_index of the leaves

rid_to_iid = {node.rid: node.iid for node in tt.sorted_wires}
leaves_node_id_to_wire_index = {
  node_rid: rid_to_iid[node_rid]
  for node_rid in tt.leaves
}
with open(node_id_to_wire_index_filepath, "w") as f:
  json.dump(leaves_node_id_to_wire_index, f)



# ls = tt.leaves_ordered()

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