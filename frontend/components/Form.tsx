"use client";

import {
  Button,
  Field,
  Fieldset,
  Flex,
  Input,
  Stack,
  Tabs,
} from "@chakra-ui/react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { CgUser, CgUserAdd } from "react-icons/cg";
import { useForm, FormProvider } from "react-hook-form";

function Form() {
  const [signingin, setSigningIn] = useState(false);
  const [signingup, setSigningUp] = useState(false);
  return (
    <Flex colorPalette="teal">
      <Tabs.Root defaultValue="members">
        <Tabs.List>
          <Tabs.Trigger value="signin">
            <CgUser />
            Sign In
          </Tabs.Trigger>
          <Tabs.Trigger value="signup">
            <CgUserAdd />
            Sign Up
          </Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="signin">
          <Fieldset.Root size="md" maxW="md">
            <Stack>
              <Fieldset.Legend>Sign In</Fieldset.Legend>
              <Fieldset.HelperText>
                Please tell us who you are
              </Fieldset.HelperText>
            </Stack>

            <Fieldset.Content>
              <Field.Root>
                <Field.Label>Number</Field.Label>
                <Input name="lnumber" type="number" />
              </Field.Root>
              <Field.Root>
                <Field.Label>Password</Field.Label>
                <Input name="lpassword" type="password" />
              </Field.Root>
              <Button
                loading={signingin}
                onClick={() => setSigningIn(!signingin)}
              >
                Sign In
              </Button>
            </Fieldset.Content>
          </Fieldset.Root>
        </Tabs.Content>
        <Tabs.Content value="signup">
          <Fieldset.Root size="md" maxW="md">
            <Stack>
              <Fieldset.Legend>Sign Up</Fieldset.Legend>
              <Fieldset.HelperText>
                Please tell us who you are
              </Fieldset.HelperText>
            </Stack>

            <Fieldset.Content>
              <Field.Root>
                <Field.Label>Number</Field.Label>
                <Input name="number" type="number" />
              </Field.Root>
              <Field.Root>
                <Field.Label>Name</Field.Label>
                <Input name="name" />
              </Field.Root>
              <Field.Root>
                <Field.Label>Surname</Field.Label>
                <Input name="surname" />
              </Field.Root>
              <Field.Root>
                <Field.Label>Password</Field.Label>
                <Input name="password" type="password" />
              </Field.Root>
              <Button
                loading={signingup}
                onClick={() => setSigningIn(!signingup)}
              >
                Sign Up
              </Button>
            </Fieldset.Content>
          </Fieldset.Root>
        </Tabs.Content>
      </Tabs.Root>
    </Flex>
  );
}

export default Form;
